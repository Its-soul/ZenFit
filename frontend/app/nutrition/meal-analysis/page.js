"use client";

import { Camera, Check, ImageUp, LoaderCircle, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import Image from "next/image";
import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { getApiErrorMessage } from "@/services/apiClient";
import { getAiHealth } from "@/services/aiService";
import { analyzeMealImageLocal, confirmMealAnalysis } from "@/services/nutritionService";

const blank={name:"",quantity:1,grams:100,nutrition:{},baseGrams:100,confidence_level:"low",top_candidates:[]};
export default function MealAnalysisPage(){
 const [health,setHealth]=useState(null),[file,setFile]=useState(null),[preview,setPreview]=useState(""),[analysis,setAnalysis]=useState(null),[foods,setFoods]=useState([]),[stage,setStage]=useState(""),[error,setError]=useState(""),[saved,setSaved]=useState(false),[trainingConsent,setTrainingConsent]=useState(false);
 useEffect(()=>{getAiHealth().then(setHealth).catch(()=>setError("Meal scanning status is unavailable. You can still enter foods manually."));},[]);
 function choose(event){const next=event.target.files?.[0]; if(!next)return; if(preview)URL.revokeObjectURL(preview); setFile(next);setPreview(URL.createObjectURL(next));setError("");setSaved(false);}
 async function analyze(){if(!file)return; setStage("Analyzing meal...");setError("");try{const result=await analyzeMealImageLocal(file);setAnalysis(result);setFoods(result.foods.map(f=>({...f,grams:f.estimated_grams,baseGrams:f.estimated_grams})));if(!result.foods.length)setFoods([{...blank}]);}catch(e){setError(getApiErrorMessage(e,"We couldn't analyze this image. You can add the foods manually."));setFoods([{...blank}]);}finally{setStage("");}}
 function edit(i,key,value){setFoods(items=>items.map((item,index)=>index===i?{...item,[key]:key==="name"?value:Number(value)}:item));}
 async function confirm(){if(!analysis){setError("Analyze a photo first so the meal can be securely confirmed.");return;}setStage("Saving meal...");try{await confirmMealAnalysis({analysis_id:analysis.analysis_id,foods:foods.map(({name,quantity,grams})=>({name,quantity,grams})),training_consent:trainingConsent});setSaved(true);setError("");}catch(e){setError(getApiErrorMessage(e,"The meal could not be saved. Please try again."));}finally{setStage("");}}
 const capability=health?.meal_scan?.overall;
 const totals=["calories","protein_g","carbs_g","fat_g","fiber_g"].reduce((result,key)=>({...result,[key]:foods.reduce((sum,food)=>sum+(Number(food.nutrition?.[key])||0)*(Number(food.grams)||0)/(food.baseGrams||food.grams||1),0)}),{});
 return <ProtectedFeaturePage title="Meal analysis" description="Upload a meal photo, review every estimate, and correct portions before saving.">
   <div className="grid gap-5 lg:grid-cols-[1fr_1.15fr]">
    <section className="panel rounded-2xl p-5">
     <div className="flex items-center gap-2"><Camera className="h-5 w-5 text-zenSage"/><h2 className="font-semibold">Meal photo</h2></div>
     {capability==="unavailable"?<p className="mt-3 rounded-xl bg-amber-400/10 p-3 text-sm text-amber-200">Automatic recognition is currently unavailable. You can still upload a photo and enter foods manually.</p>:capability==="partial"?<p className="mt-3 text-sm text-muted">We can identify some common foods. Please review the result before saving.</p>:null}
     <label className="mt-4 flex min-h-64 cursor-pointer items-center justify-center overflow-hidden rounded-2xl border border-dashed border-white/20 bg-black/20">
      {preview?<Image unoptimized width={800} height={600} src={preview} alt="Meal preview" className="max-h-80 w-full object-contain"/>:<span className="flex flex-col items-center gap-2 text-sm text-muted"><ImageUp/>Choose or capture a JPEG, PNG, or WebP image</span>}
      <input className="hidden" type="file" accept="image/jpeg,image/png,image/webp" capture="environment" onChange={choose}/>
     </label>
     <Button className="mt-4 w-full" disabled={!file||!!stage} onClick={analyze}>{stage?<LoaderCircle className="h-4 w-4 animate-spin"/>:<ImageUp className="h-4 w-4"/>}{stage||"Analyze meal"}</Button>
    </section>
    <section className="panel rounded-2xl p-5"><h2 className="font-semibold">Review foods</h2><p className="mt-1 text-sm text-muted">Image portions are estimates. Change names, pieces, or grams before confirming.</p>
     <div className="mt-4 space-y-3">{foods.map((food,i)=><div key={i} className="rounded-xl border border-white/10 p-3"><div className="grid gap-2 sm:grid-cols-[1fr_90px_110px_40px]"><Input value={food.name} placeholder="Food name" onChange={e=>edit(i,"name",e.target.value)}/><Input aria-label="Quantity" type="number" min="0.1" step="0.1" value={food.quantity} onChange={e=>edit(i,"quantity",e.target.value)}/><Input aria-label="Grams" type="number" min="1" value={food.grams} onChange={e=>edit(i,"grams",e.target.value)}/><button aria-label="Remove food" onClick={()=>setFoods(v=>v.filter((_,x)=>x!==i))}><Trash2 className="h-4 w-4 text-muted"/></button></div>{food.food_confidence?<p className="mt-2 text-xs text-muted">Recognition confidence: <span className={food.confidence_level==="high"?"text-zenSage":food.confidence_level==="medium"?"text-amber-200":"text-coralGlow"}>{food.confidence_level}</span> · Portion confidence: {Math.round((food.portion_confidence||0)*100)}%</p>:null}{food.confidence_level!=="high"&&food.top_candidates?.length?<div className="mt-2 flex flex-wrap gap-2"><span className="text-xs text-muted">Is this:</span>{food.top_candidates.map(candidate=><button key={candidate.label} className="rounded-full bg-white/10 px-2 py-1 text-xs" onClick={()=>edit(i,"name",candidate.label)}>{candidate.label.replaceAll("_"," ")} ({Math.round(candidate.confidence*100)}%)</button>)}<button className="rounded-full bg-white/10 px-2 py-1 text-xs" onClick={()=>edit(i,"name","")}>Something else</button></div>:null}</div>)}</div>
     <Button variant="secondary" className="mt-3" onClick={()=>setFoods(v=>[...v,{...blank}])}><Plus className="h-4 w-4"/>Add food</Button>
     <div className="mt-4 grid grid-cols-2 gap-2 rounded-xl bg-white/5 p-3 text-sm sm:grid-cols-5"><span>{Math.round(totals.calories)} kcal</span><span>{totals.protein_g.toFixed(1)}g protein</span><span>{totals.carbs_g.toFixed(1)}g carbs</span><span>{totals.fat_g.toFixed(1)}g fat</span><span>{totals.fiber_g.toFixed(1)}g fiber</span></div>
     {analysis?.warnings?.length?<div className="mt-4 rounded-xl bg-white/5 p-3 text-sm text-muted">{analysis.warnings.join(" ")}</div>:null}
     {error?<p className="mt-4 text-sm text-coralGlow">{error}</p>:null}{saved?<p className="mt-4 flex items-center gap-2 text-sm text-zenSage"><Check className="h-4 w-4"/>Meal saved and today&apos;s totals were updated.</p>:null}
     <label className="mt-4 flex items-start gap-2 text-xs text-muted"><input type="checkbox" checked={trainingConsent} onChange={e=>setTrainingConsent(e.target.checked)}/><span>Allow this meal image to be considered for future anonymized recognition improvement. Off by default; current implementation records consent but does not retain the image for training.</span></label>
     <Button className="mt-4 w-full" disabled={!foods.length||!!stage||saved} onClick={confirm}>Confirm and save meal</Button>
    </section>
   </div>
  </ProtectedFeaturePage>;
}
