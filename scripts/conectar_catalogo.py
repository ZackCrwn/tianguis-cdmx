from pathlib import Path
p=Path("index.html")
s=p.read_text(encoding="utf-8")
before="updateDays();loadMap();rerender();if(!official.length){sync().catch(err=>console.warn(err))}"
after="""updateDays();loadMap();rerender();
(async function loadPublishedCatalog(){
 try{
  const r=await fetch('./catalogo.json?v=3',{cache:'no-store'});
  if(!r.ok)throw Error('No se ha publicado catalogo.json');
  const payload=await r.json();
  const features=Array.isArray(payload)?payload:payload.records||payload.features||[];
  const items=features.map((f,i)=>f.properties?convertFeature(f,i,'Tianguis'):f);
  if(!items.length)throw Error('Catálogo vacío');
  official=items;store('tx_official',official);rerender();
  $('#notice').textContent='Catálogo oficial cargado: '+items.length+' registros. Horarios sujetos a verificación.';
 }catch(err){
  if(!official.length)$('#notice').textContent='Catálogo pendiente de publicación. Puedes importar CSV o GeoJSON desde el botón de la portada. '+err.message;
 }
})();"""
if before in s:
 p.write_text(s.replace(before,after),encoding="utf-8")
 print("index.html patched")
elif "loadPublishedCatalog" in s: print("Already patched")
else:raise ValueError("Original app initialization not found")
