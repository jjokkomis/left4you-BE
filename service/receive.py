# service/receive.py
from typing import Dict, Any, List, Optional, Set, Tuple
import math
from fastapi import HTTPException
from data import receive as data

# ===== 0) 지역 매핑 (한글 → 코드) =====
REGION_TO_CITY = {
    "서울":"SEOUL","부산":"BUSAN","대구":"DAEGU","인천":"INCHEON","광주":"GWANGJU",
    "제주":"JEJU","대전":"DAEJEON","경기":"GYEONGGI","울산":"ULSAN","세종":"SEJONG"
}

# ===== 1) 점수 가중치 =====
W_CITY, W_THEME, W_EMOTION, W_TIME, W_WALK, W_QUALITY = 2.0, 1.5, 1.2, 0.7, 0.6, 0.3

# ===== 2) BBOX(겹침 수정 반영) =====
CITY_BBOX = {
    "SEOUL":   (37.35, 37.72, 126.76, 127.18),
    "BUSAN":   (35.02, 35.35, 129.00, 129.25),
    "INCHEON": (37.30, 37.60, 126.35, 126.80),
    "DAEGU":   (35.70, 36.00, 128.40, 128.80),
    "DAEJEON": (36.20, 36.50, 127.20, 127.50),
    "GWANGJU": (35.05, 35.25, 126.70, 127.05),
    "ULSAN":   (35.40, 35.70, 129.20, 129.50),
    "SEJONG":  (36.45, 36.65, 127.20, 127.40),
    "GYEONGGI":(36.80, 38.30, 126.30, 127.60),  # 동쪽 축소
    "GANGWON": (37.00, 38.60, 127.60, 129.60),  # 서쪽부터 시작
    "JEJU":    (33.10, 33.60, 126.10, 126.95),
}

# ===== 3) 유틸 =====
def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0; to_rad = math.pi/180.0
    dlat = (lat2 - lat1) * to_rad; dlon = (lon2 - lon1) * to_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1*to_rad)*math.cos(lat2*to_rad)*math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def _compute_distance_km(places: List[Dict[str,Any]]) -> float:
    total = 0.0
    ps = sorted(places, key=lambda x: x["seq"])
    for i in range(len(ps)-1):
        a, b = ps[i], ps[i+1]
        if a["latitude"] and a["longitude"] and b["latitude"] and b["longitude"]:
            total += _haversine(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
    return round(total, 2)

def _kw(name: str) -> str: return (name or "").lower()

def _bucket_minutes(place_name: str) -> Tuple[int,int]:
    n = _kw(place_name)
    if any(k in n for k in ["카페","cafe","브런치","식당","맛집"]): return (45,90)
    if any(k in n for k in ["미술관","museum","박물관","gallery","갤러리","도서관","서점"]): return (60,120)
    if any(k in n for k in ["공원","park","산책","둘레길","trail","해변","비치","강변","호수"]): return (30,60)
    if any(k in n for k in ["클라이밍","서핑","카약","vr","액티비티","체험","암벽"]): return (90,180)
    return (20,40)

def _derive_features(course: Dict[str,Any], places: List[Dict[str,Any]]) -> Dict[str,Any]:
    distance_km = _compute_distance_km(places)
    walking_min = (distance_km / 4.5) * 60.0
    dwell_min = sum((sum(_bucket_minutes(p.get("place_name",""))) / 2.0) for p in places)
    duration_min = int(round(walking_min + dwell_min))
    walk_ratio = 0.0 if duration_min == 0 else walking_min / duration_min

    if distance_km >= 6.0 or walk_ratio >= 0.6: walk_type = "MANY"
    elif distance_km >= 3.0 or walk_ratio >= 0.3: walk_type = "EASY"
    else: walk_type = "SIT"

    place_text = " ".join(p.get("place_name","") for p in places)
    full_text = f"{course.get('name','')} {course.get('content','')} {place_text}".lower()
    time_pref = "HALF" if duration_min < 240 else ("ALL" if duration_min <= 540 else "ALL")
    if any(k in full_text for k in ["야경","night","밤","루프탑","bar","펍","pub","분수"]):
        time_pref = "NIGHT"

    # centroid → bbox
    city = None
    if places:
        lat = sum(p["latitude"] for p in places)/len(places)
        lon = sum(p["longitude"] for p in places)/len(places)
        for c,(la,lb,lo,hi) in CITY_BBOX.items():
            if la <= lat <= lb and lo <= lon <= hi:
                city = c; break

    return {"city": city, "distance_km": round(distance_km,2), "duration_min": duration_min, "walk_type": walk_type, "time": time_pref}

def _jaccard(a:Set[str], b:Set[str]) -> float:
    if not a and not b: return 0.0
    u = len(a|b); return 0.0 if u==0 else len(a&b)/u

def _walk_sim(user: Optional[str], course: Optional[str]) -> float:
    if not user or not course: return 0.0
    if user == course: return 1.0
    return 0.5 if {user,course} in ({"MANY","EASY"},{"EASY","SIT"}) else 0.2

def _norm(v: Optional[str]) -> Optional[str]:
    return None if v is None else v.strip().upper()

# ===== 4) 테마/감정 간단 추출 (이름/콘텐츠/장소명 키워드) =====
THEME_RULES = {
  "ART":["미술관","박물관","gallery","전시","갤러리"],
  "LIBRARY":["도서관","서점","book"],
  "ANIMAL":["동물원","캣카페","애견"],
  "NATUAL":["공원","숲","정원","산","해변","호수","강"],
  "MEDITATION":["사찰","템플","명상","성당","절"],
  "HISTORY":["고궁","유적","한옥","전통시장","문화재"],
  "ACTIVITY":["클라이밍","서핑","카약","VR","체험","볼더링","자전거"],
  "WALK":["산책","둘레길","트레일","하이킹","한강"]
}
EMOTION_RULES = {
  "CALM":["공원","숲","정원","호수","강변","서점","도서관","카페"],
  "COMFORT":["카페","브런치","한강","공원","야외"],
  "HAPPY":["축제","놀이","해변","야경","시장"],
  "MISS":["한옥","고궁","레트로","전통","골목"],
  "COURAGE":["클라이밍","서핑","번지","암벽"],
  "WORRY":[]
}
def _extract_themes_emotions(course: Dict[str,Any], places: List[Dict[str,Any]]) -> Tuple[Set[str],Set[str]]:
    text = (course.get("name","") + " " + course.get("content","") + " " + " ".join(p.get("place_name","") for p in places)).lower()
    T,E=set(),set()
    for k,keys in THEME_RULES.items():
        if any(kw.lower() in text for kw in keys): T.add(k)
    for k,keys in EMOTION_RULES.items():
        if any(kw.lower() in text for kw in keys): E.add(k)
    return T,E

# ===== 5) 추천 점수 =====
def _score(traits: Dict[str,Any], derived: Dict[str,Any], themes:Set[str], emotions:Set[str], rating_avg: Optional[float], rating_cnt:int)->float:
    city_match = 1.0 if derived.get("city") and traits.get("CITY")==derived["city"] else 0.0
    theme_j = _jaccard(set(traits.get("THEME",[])), themes)
    emos = traits.get("EMOTION", [])
    emo_hit = 0.0 if not emos else sum(1 for e in emos if e in emotions)/len(emos)
    time_match = 1.0 if traits.get("TIME") and traits["TIME"]==derived.get("time") else 0.0
    walk_u = _norm(traits.get("WALK_TYPE")); walk_u = "EASY" if walk_u=="ESAY" else walk_u
    walk_match = _walk_sim(walk_u, derived.get("walk_type"))
    if rating_avg is None or rating_cnt==0: quality=0.0
    else:
        C,m=4.0,8
        bayes=(rating_cnt/(rating_cnt+m))*rating_avg+(m/(rating_cnt+m))*C
        quality=(bayes-3.0)/2.0
    return W_CITY*city_match+W_THEME*theme_j+W_EMOTION*emo_hit+W_TIME*time_match+W_WALK*walk_match+W_QUALITY*quality

# ===== 6) GiftData 생성 =====
def _short_area(name:str)->str:
    if not name: return ""
    s = name.replace("한강공원","").replace("해변","").replace("공원","").replace("미술관","").replace("박물관","").strip()
    # 공백 전 첫 토큰 우선
    return s.split()[0] if " " in s and s.split()[0] else (s or name)

def _build_location_label(places: List[Dict[str,Any]])->str:
    if not places: return ""
    ps = sorted(places, key=lambda x:x["seq"])
    start = _short_area(ps[0]["place_name"])
    end = _short_area(ps[-1]["place_name"])
    if start and end and start!=end:
        return f"{start} -> {end}"
    # 단일/동일이면 유형 라벨로
    return "공원" if any("공원" in p["place_name"] for p in ps) else start or end

def _describe_place(place_name:str, derived:Dict[str,Any])->str:
    n = _kw(place_name)
    lines: List[str] = []
    if any(k in n for k in ["한강","공원","park","산책","둘레길","하천","강변","호수"]):
        lines += ["산책로 감상 & 포토스폿", "돗자리 피크닉/벗꽃·장미 시즌 추천"]
    if any(k in n for k in ["카페","cafe","브런치"]):
        lines += ["브런치/디저트로 휴식", "창가 좌석 추천"]
    if any(k in n for k in ["미술관","museum","박물관","gallery","갤러리"]):
        lines += ["전시 관람으로 조용한 힐링"]
    if any(k in n for k in ["시장","food","마켓"]):
        lines += ["로컬 먹거리 탐방"]
    if derived.get("time")=="NIGHT":
        lines += ["야경 감상 포인트 체크"]
    if not lines:
        lines = ["가볍게 둘러보기", "근처 카페/편의시설 이용"]
    # 숫자 정보 보강(짧게)
    dist = derived.get("distance_km"); dur = derived.get("duration_min")
    tail = []
    if dist: tail.append(f"예상 이동 {dist}km")
    if dur:  tail.append(f"예상 소요 {dur}분")
    if tail: lines.append(" / ".join(tail))
    return "<br />".join(lines)

def _gift_from(course:Dict[str,Any], places:List[Dict[str,Any]], derived:Dict[str,Any])->Dict[str,Any]:
    ps = sorted(places, key=lambda x:x["seq"])
    # 3 스테이지 선택: 처음/중간/마지막 (중복 방지)
    idxs = list({0, len(ps)//2, len(ps)-1}) if len(ps)>=3 else list(range(len(ps)))
    idxs = sorted(set(i for i in idxs if 0<=i<len(ps)))[:3]

    stages = []
    location_label = _build_location_label(ps)
    for i,idx in enumerate(idxs):
        p = ps[idx]
        # 첫 스테이지는 경로 라벨, 나머지는 유형 또는 지명
        if i==0:
            loc = location_label or _short_area(p["place_name"])
        else:
            loc = ("공원" if "공원" in p["place_name"] else _short_area(p["place_name"]))
        stages.append({
            "location": loc,
            "place": p["place_name"],
            "description": _describe_place(p["place_name"], derived),
            "latitude": p.get("latitude"),
            "longitude": p.get("longitude")
        })

    # 타이틀 생성(간단 템플릿)
    title_bits = []
    if any("공원" in x["place_name"] or "한강" in x["place_name"] for x in ps): title_bits.append("공원")
    if derived.get("time")=="NIGHT": title_bits += ["야경"]
    if derived.get("walk_type")=="EASY": title_bits.append("힐링")
    title = " & ".join(dict.fromkeys(title_bits)) + " 코스" if title_bits else course.get("name") or "추천 코스"

    return {"name": course.get("name") or title, "courses": stages}

# ===== 7) 메인 =====
def recommend_giftdata(user_id: int, city: Optional[str], region: Optional[str]) -> Optional[Dict[str,Any]]:
    # 7.1 입력 정규화 (region 한글 → city 코드)
    if not city and region:
        city = REGION_TO_CITY.get(region)
    if not city:
        raise HTTPException(status_code=400, detail="city_or_region_required")

    bbox = CITY_BBOX.get(city)
    if not bbox:
        raise HTTPException(status_code=400, detail="unknown_city")

    # 7.2 설문 로드
    survey = data.load_survey(user_id)
    traits = {
        "CITY": city,
        "THEME": [_norm(r["value"]) for r in survey if r["type"]=="THEME"],
        "EMOTION": [_norm(r["value"]) for r in survey if r["type"]=="EMOTION"],
        "TIME": _norm(next((r["value"] for r in survey if r["type"]=="TIME"), None)),
        "WALK_TYPE": _norm(next((r["value"] for r in survey if r["type"]=="WALK_TYPE"), None)),
    }
    if traits["WALK_TYPE"] == "ESAY": traits["WALK_TYPE"] = "EASY"  # 오타 보정

    # 7.3 후보(도시 bbox & 이미 받은 코스 제외)
    lat_min, lat_max, lon_min, lon_max = bbox
    candidate_ids = data.find_candidate_course_ids_by_city_bbox(
        user_id=user_id, lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max
    )
    if not candidate_ids:
        return None

    courses = data.load_courses(candidate_ids)
    places_map = data.load_places_by_course_ids(candidate_ids)
    rating_map = data.load_rating_by_course_ids(candidate_ids)

    best_id, best_score, best_tie, best_pack = None, -1e9, (-1,-1), None
    for cid in candidate_ids:
        course = courses.get(cid); places = places_map.get(cid, [])
        if not course or not places: continue

        derived = _derive_features(course, places)
        # 도시 최종 검증(요청 도시와 다르면 제외)
        if derived.get("city") != city: continue

        themes, emotions = _extract_themes_emotions(course, places)
        avg, cnt = rating_map.get(cid, (None, 0))
        s = _score(traits, derived, themes, emotions, avg, cnt)
        tiebreak = (cnt or 0, int(course.get("created_at_ts", 0)) if isinstance(course.get("created_at_ts",0), int) else 0)

        if (s, tiebreak) > (best_score, best_tie):
            best_id, best_score, best_tie = cid, s, tiebreak
            giftdata = _gift_from(course, places, derived)
            best_pack = giftdata

    return best_pack
