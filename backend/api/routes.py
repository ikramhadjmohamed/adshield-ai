from fastapi import APIRouter, Form, File, UploadFile
from models.schemas import Advertisement, TrustReport
from agents.url_agent import analyze_url
from agents.text_agent import analyze_text
from agents.image_agent import analyze_image
from agents.brand_agent import analyze_brand
from agents.decision_agent import make_decision

router = APIRouter()


@router.post("/review-ad", response_model=TrustReport)
async def review_ad(
    brand_name: str = Form(...),
    headline: str = Form(...),
    description: str = Form(...),
    landing_url: str = Form(...),
    image: UploadFile | None = File(None),
):
    image_bytes = await image.read() if image is not None else None

    ad = Advertisement(
        brand_name=brand_name,
        headline=headline,
        description=description,
        landing_url=landing_url,
        image_bytes=image_bytes,
    )

    url_result = analyze_url(ad.brand_name, str(ad.landing_url))
    text_result = analyze_text(ad.brand_name, ad.headline, ad.description)
    image_result = analyze_image(ad.image_bytes)
    brand_result = analyze_brand(ad.brand_name, ad.headline, ad.description)

    agent_results = [url_result, text_result, image_result, brand_result]

    report = make_decision(ad.ad_id, agent_results)
    return report