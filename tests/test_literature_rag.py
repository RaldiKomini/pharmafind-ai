from types import SimpleNamespace

import pytest

from app.clients.pubmed_client import (
    PubMedPaperSummary,
    PubMedSearchResult,
    parse_pubmed_xml,
)
from app.llm.evidence_synthesizer import (
    GroundedClaimOutput,
    GroundedEvidenceOutput,
    generate_grounded_evidence_synthesis,
)
from app.pipeline.literature_retriever import (
    LiteratureRetrievalConfig,
    cosine_similarity,
    retrieve_relevant_literature,
)


PUBMED_XML = b"""<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>123</PMID>
      <Article>
        <ArticleTitle>Drug and <i>event</i> evidence</ArticleTitle>
        <Abstract>
          <AbstractText Label="BACKGROUND">Background text.</AbstractText>
          <AbstractText Label="RESULTS">Result <b>details</b>.</AbstractText>
        </Abstract>
        <Journal>
          <Title>Safety Journal</Title>
          <JournalIssue><PubDate><Year>2025</Year><Month>Dec</Month></PubDate></JournalIssue>
        </Journal>
        <PublicationTypeList><PublicationType>Observational Study</PublicationType></PublicationTypeList>
      </Article>
    </MedlineCitation>
    <PubmedData><ArticleIdList><ArticleId IdType="doi">10.1/example</ArticleId></ArticleIdList></PubmedData>
  </PubmedArticle>
</PubmedArticleSet>"""


def test_pubmed_xml_parser_returns_sectioned_abstract_and_metadata():
    papers = parse_pubmed_xml(PUBMED_XML, ["123"])

    assert len(papers) == 1
    paper = papers[0]
    assert paper.title == "Drug and event evidence"
    assert paper.abstract == "BACKGROUND: Background text.\nRESULTS: Result details."
    assert paper.source == "Safety Journal"
    assert paper.pub_date == "2025 Dec"
    assert paper.doi == "10.1/example"
    assert paper.publication_types == ("Observational Study",)


def test_cosine_similarity_validates_vectors():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        cosine_similarity([], [])


class FakePubMedClient:
    def search_papers(self, config):
        return PubMedSearchResult(
            total_result_count=42,
            papers=[
                PubMedPaperSummary(pmid="1", title="First", abstract="Less relevant"),
                PubMedPaperSummary(pmid="2", title="Second", abstract="Most relevant"),
            ],
        )


class FakeEmbeddings:
    def create(self, **kwargs):
        # query, paper 1, paper 2: paper 2 is closest to the query.
        return SimpleNamespace(
            data=[
                SimpleNamespace(embedding=[1.0, 0.0]),
                SimpleNamespace(embedding=[0.0, 1.0]),
                SimpleNamespace(embedding=[0.9, 0.1]),
            ]
        )


class FakeResponses:
    def __init__(self, output):
        self.output = output

    def parse(self, **kwargs):
        return SimpleNamespace(output_parsed=self.output)


class FakeOpenAI:
    def __init__(self, output=None):
        self.embeddings = FakeEmbeddings()
        self.responses = FakeResponses(output)


def test_retrieval_semantically_reranks_candidates_and_preserves_total_hits():
    result = retrieve_relevant_literature(
        "Drug",
        "Event",
        LiteratureRetrievalConfig(candidate_count=25, max_results=1, use_embeddings=True),
        pubmed_client=FakePubMedClient(),
        openai_client=FakeOpenAI(),
    )

    assert result.total_result_count == 42
    assert result.ranking_method == "semantic_embedding"
    assert [paper.pmid for paper in result.papers] == ["2"]
    assert result.papers[0].relevance_score is not None


def test_grounded_synthesis_rejects_model_generated_pmid():
    paper = PubMedPaperSummary(pmid="123", title="Paper", abstract="Abstract evidence")
    output = GroundedEvidenceOutput(
        summary="Summary",
        overall_stance="supports",
        claims=[GroundedClaimOutput(text="Claim", stance="supports", pmids=["999"])],
        limitations=[],
    )

    with pytest.raises(ValueError, match="outside the retrieved set"):
        generate_grounded_evidence_synthesis(
            "Drug",
            "Event",
            [paper],
            client=FakeOpenAI(output),
        )


def test_grounded_synthesis_returns_validated_claims():
    paper = PubMedPaperSummary(pmid="123", title="Paper", abstract="Abstract evidence")
    output = GroundedEvidenceOutput(
        summary="Summary",
        overall_stance="unclear",
        claims=[GroundedClaimOutput(text="Claim", stance="unclear", pmids=["123"])],
        limitations=["Abstract only"],
    )
    synthesis = generate_grounded_evidence_synthesis(
        "Drug",
        "Event",
        [paper],
        client=FakeOpenAI(output),
    )

    assert synthesis is not None
    assert synthesis.claims[0].pmids == ["123"]
