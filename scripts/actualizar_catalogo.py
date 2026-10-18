import json, urllib.request, pathlib, csv, io, time
BASE="https://datos.cdmx.gob.mx"
API=BASE+"/api/3/action/package_show?id=tianguis-de-la-ciudad-de-mexico"
headers={"User-Agent":"TianguisCDMX/1.0 (public data synchronization)","Accept":"application/json, text/plain, */*"}
def get(url):
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=55) as r:return r.read()
meta=json.loads(get(API))
assert meta.get("success"),"CKAN returned unsuccessful status"
resources=meta["result"]["resources"]
options=sorted([r for r in resources if str(r.get("format","")).lower() in ("geojson","csv") and "diccionario" not in str(r.get("name","")).lower()],key=lambda r:0 if str(r.get("format","")).lower()=="geojson" else 1)
errors=[]
for r in options:
    try:
        raw=get(r["url"]); fmt=str(r.get("format","")).lower()
        if fmt=="geojson":
            j=json.loads(raw.decode("utf-8-sig")); features=j["features"] if isinstance(j,dict) and j.get("type")=="FeatureCollection" else []
        else:
            rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
            features=[{"type":"Feature","properties":v,"geometry":None} for v in rows]
        if len(features)<100:raise ValueError("Unexpectedly small result: "+str(len(features)))
        out={"source":"SEDECO / datos.cdmx.gob.mx","records":[{"type":"Feature","properties":f.get("properties",{}),"geometry":f.get("geometry")} for f in features]}
        pathlib.Path("catalogo.json").write_text(json.dumps(out,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
        print("Saved",len(features),"records from",r["url"])
        break
    except Exception as exc:errors.append(str(exc))
else:raise RuntimeError("Could not retrieve official catalog: "+"; ".join(errors))
