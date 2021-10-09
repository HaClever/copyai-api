from fastapi import APIRouter
from selenium_bots import CopyAiSelenium
from schemas import OneFieldOption, TwoFieldOption

copyai = CopyAiSelenium()

router = APIRouter()


@router.get("/login")
async def login_to_copyai():
    """Логин в Copy.ai"""
    copyai.log_in_if_not_loggined()


@router.post("/one_field_tools")
async def use_one_field_tool(option: OneFieldOption) -> dict:
    """- Для работы с инструментами, у которых одно поле
    - **Доступные опции**: Instagram Captions, Hashtags, Microcopy, Event Copy, Question Generator, Follow Up Email,
    Confirmation Emails, Video Titles, Carousel Post, Captions, Video Intro Hook, Relatable Experiences,
    Brainstorm Topics, Bullet Points, Keyword Generator, Add Emoji to List, Simplify Sentence, Verb Booster,
    Adjective Accelerator, Analogy Generator, Two Sentence Stories, Hero Story Intro, Cliffhanger,
    Explain In Plain English, Passive to Active Voice, Name Generator, Startup Ideas, Shower Thoughts, Clubhouse Bio
    - **Список тонов**:  Friendly, Laxury, Relaxed, Professional, Bold, Adventurous, Witty, Persuasive, Empathetic
    """
    copyai.log_in_if_not_loggined()
    copyai.enter_project()
    copyai.copyai_change_language(option.tone)
    copyai.copyai_select_option(option.option.value)
    return {"texts": copyai.copyai_get_response(option.field_value)}


@router.post("/two_field_tools")
async def use_two_field_tool(option: TwoFieldOption) -> dict:
    """- Для работы с инструментами, у которых два поля
    - **Доступные опции**: Product Descriptions, Facebook Primary Text, Facebook Listicle, Facebook Headlines,
    Facebook Link descriptions, Google Headlines, Google Descriptions, Instagram Product Showcase,
    Linkedln Text Ads, General Ad Copy, Ad Copy Variants, Value Proposition, Motto Generator, Brand Mission,
    Brand Voice, Audience Refiner, Landing Page Hero Text, Subheader Text, Blog Ideas, Blog Intros, Blog Outline,
    Bullet Point to Paragraph, Bullet Points to Blog, Blog Titles, Blog Titles - Listicles, Listicles, Meta Descriptions,
    Testimonial Rewriter, Social Proof Text, Catchy Email Subject Lines, Welcome Email, Thank You Note,
    Cancellation Email, Launch Your Product, Short Text Hook, Product Showcase, Video Call to Action,
    Youtube Description Intro, Keyword Genrator, Pain-Agitate-Solution, AIDA Copywriting, Before-After-Brige,
    Feature-Advantage-Benefit, Problem-Promise-Proof-Proposal, QUEST Copywriting, Feature to Benefit, Marketing Angels,
    Change Tone, Sentence Rewriter, Essay Outline, Essay Intro, Bullet Points to Essay, Rewrite with KeyWords,
    Press Release Intros, Hero Story Villian, Viral Ideas, Grows Ideas, Next Producs, Cover Letter, Resume Bullet Points,
    Love Letter, Mother's Day, Birsday Cards
    - **Список тонов**:  Friendly, Laxury, Relaxed, Professional, Bold, Adventurous, Witty, Persuasive, Empathetic
    """
    copyai.log_in_if_not_loggined()
    copyai.enter_project()
    copyai.copyai_change_language(option.tone)
    copyai.copyai_select_option(option.option.value)
    return {
        "texts": copyai.copyai_get_response(
            option.main_field_value, option.secondary_field_value
        )
    }
