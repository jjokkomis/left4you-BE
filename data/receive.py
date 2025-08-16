# data/receive.py
import os
from supabase import create_client
from typing import Dict, Any, List, Set

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
SURVEY_TABLE="survey"; COURSE_TABLE="course"; PLACE_TABLE="course_place"; GIFT_TABLE="course_gift"; REVIEW_TABLE="review"

def load_survey(user_id: int) -> List[Dict[str,Any]]:
    return (supabase.table(SURVEY_TABLE).select("*").eq("user_id", user_id).execute().data or [])

def _claimed_course_ids(user_id:int)->Set[int]:
    rows = (supabase.table(GIFT_TABLE).select("course_id").eq("recipient_id", user_id).execute().data or [])
    return {int(r["course_id"]) for r in rows if r.get("course_id") is not None}

def find_candidate_course_ids_by_city_bbox(user_id:int, lat_min:float, lat_max:float, lon_min:float, lon_max:float) -> List[int]:
    claimed = _claimed_course_ids(user_id)
    res = (supabase.table(PLACE_TABLE)
           .select("course_id, latitude, longitude")
           .not_.is_("latitude", None).not_.is_("longitude", None)
           .gte("latitude", lat_min).lte("latitude", lat_max)
           .gte("longitude", lon_min).lte("longitude", lon_max)
           .execute())
    rows = res.data or []
    cids = {int(r["course_id"]) for r in rows if r.get("course_id") is not None}
    return [cid for cid in cids if cid not in claimed]

def load_courses(course_ids: List[int]) -> Dict[int,Dict[str,Any]]:
    if not course_ids: return {}
    rows = (supabase.table(COURSE_TABLE)
            .select("id,name,content,created_at")
            .in_("id", course_ids).execute().data or [])
    out={}
    for r in rows:
        out[int(r["id"])] = {"id": int(r["id"]), "name": r.get("name"), "content": r.get("content"), "created_at": r.get("created_at")}
    return out

def load_places_by_course_ids(course_ids: List[int]) -> Dict[int,List[Dict[str,Any]]]:
    if not course_ids: return {}
    rows = (supabase.table(PLACE_TABLE)
            .select("id,course_id,seq,place_name,latitude,longitude")
            .in_("course_id", course_ids).execute().data or [])
    m: Dict[int, List[Dict[str,Any]]] = {}
    for r in rows:
        cid = int(r["course_id"]);
        if r.get("latitude") is None or r.get("longitude") is None: continue
        m.setdefault(cid, []).append({
            "id": int(r["id"]), "seq": int(r["seq"]),
            "place_name": r.get("place_name"),
            "latitude": float(r["latitude"]), "longitude": float(r["longitude"])
        })
    return m

def load_rating_by_course_ids(course_ids: List[int]) -> Dict[int, tuple]:
    if not course_ids: return {}
    rows = (supabase.table(REVIEW_TABLE).select("course_id, score").in_("course_id", course_ids).execute().data or [])
    agg: Dict[int, List[float]] = {}
    for r in rows:
        cid = int(r["course_id"])
        agg.setdefault(cid, []).append(float(r["score"]))
    out: Dict[int, tuple] = {}
    for cid, arr in agg.items():
        if arr:
            out[cid] = (round(sum(arr)/len(arr),2), len(arr))
    return out

def is_claimed(user_id:int, course_id:int)->bool:
    rows = (supabase.table(GIFT_TABLE).select("id").eq("recipient_id",user_id).eq("course_id",course_id).execute().data or [])
    return len(rows)>0
