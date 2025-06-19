Given some text, split it into paragraphs and translate to {target_language}.
First level of splitting is some short paragraphs, each paragraph consists of some (usually more than  one, but for dialogs it maybe one and depends on how many sentences each person says) sentences. Each paragraph supposed to have at least one full sentence.
If the text has been already splitted by paragraphs, keep this splitting as is. Double new line in the text should be considered as a new paragraph.

Each paragraph might  be spitted further, to syntagmas, where each syntagma  may be either short sentence, or some part of sentence that might be pronounced with one breath and memorized without big amount of repetitions.
When translation, try to do keep the order of the words from the source language sentence, event it might sound not natural, but without loosing of sense. For phraselogismes, that might be difficult to understand,  add to the translations some explanation in parentheses. 

''' Example
Initial text:
    Adriyano, sarışın, uzun boylu, gözleri yeşil ile mavi arası, çok yakışıklı bir gençti. Üniversite mezunuydu. Devlet, turizm mevsiminde, ona, iyi İngilizce bildiği için turistik otellerde görev veriyordu. Bu yıl, yine, Mamai'deki bir büyük otelde görevliydi. Adriyano, iki yıl önce ailesinin ısrarı ile güzel bir kızla evlenmişti. Karısı bu yıl üniversiteyi bitiriyordu. Karısını seviyordu. 
    Ama, Adriano, otellerde çalışmaya başladıktan sonra, sanki huyunu değiştirmişti. Her turizm mevsiminde birkaç defa yabancı bir kıza tutuluyor, onu öpüyor, ama ona açılmıyor, başka bir şey de söylemiyor, günlere kendine işkence ediyordu.
    
Output: (empty line here is a new paragraph)
    Adriano, sarışın, uzun boylu (Адриано, светловолосый, высокий: boy — рост, boylu — имеющий рост), gözleri yeşil ile mavi arası (с зелено-голубыми глазами: его глаза между зелеными и голубыми), çok yakışıklı bir gençti (был очень красивым молодым человеком). Üniversite mezunuydu (он был выпускником университета). Devlet, turizm mevsiminde, ona (государство в туристическом сезоне ему), iyi İngilizce bildiği için (за то, что он хорошо знает английский) turistik otellerde görev veriyordu (давало работу: обязанности, обязанности в туризме). Bu yıl, yine, Manna’daki bir büyük otelde görevliydi (он работал в большом отеле в Манаве /курортный город в Румынии; görevli — работник, сотрудник).


    Ama, Adriano, otellerde çalışmaya başladıktan sonra (однако после того, как Адриано начал работать в отелях), sanki huyunu değiştirmişti (словно изменил свой характер). Her turizm mevsiminde birkaç defa yabancı bir kıza tutuluyor (он в туристический сезон несколько раз влюблялся в иностранную девушку), onu öpüyor (он ее целовал), ama ona açılmıyor (но ей не открывался: не мог сказать ей, что не сможет жить), başka bir şey de söylemiyor (не мог ей сказать что-то еще), günlere kendine içkence ediyordu (мучил себя теми днями: «себе напоминал те дни»).
```


For final output use format using schema for class BilingualText like this:
```python

class BiLingualSyntagma(BaseModel):
    """In linguistics, a syntagma is an elementary constituent segment within a text.
    Such a segment can be a phoneme, a word, a grammatical phrase, a sentence, may be either short sentence, 
    or some part of sentence that might be pronounced with one breath and memorized without big amount of repetitions.
    This class represents a bilingual syntagma, which contains a source text and its translation.
    """
    source_text: str = Field(..., description="The source text in the original language")
    target_text: str = Field(None, description="The translated text in the target language")

class BilingualParagraph(BaseModel):

    """
   Paragraph containing bilingual sintagmas.
    """
    Sintagmas: List[BiLingualSyntagma] = Field(
        ...,
        description="A list of bilingual sintagmas, each containing source and target texts"
    )

class BilingualText(BaseModel):
    paragraphs: List[BilingualParagraph] = Field(
        ...,
        description="A list of bilingual paragraphs, each containing multiple sintagmas"
    )
    
    source_language: str = Field(
        ...,
        description="The language of the source text"
    )
    target_language: str = Field(
        ...,
        description="The language of the target text, if available"
    )
```
