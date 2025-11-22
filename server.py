# api/server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import QueryRequest, QueryResponse, SourceChunk
from api.retrieval import answer_query

# THIS is what uvicorn is looking for:
# api/server.py

from fastapi import FastAPI

# THIS must exist at top level
app = FastAPI(
    title="Test App",
    description="Minimal app to verify Uvicorn import works.",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"message": "Server is running correctly"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/query", response_model=QueryResponse)
def query_manual(body: QueryRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = answer_query(body.question)

    sources = [
        SourceChunk(
            text=c["text"],
            chapter=c["chapter"],
            page=c["page"],
            score=c["score"],
        )
        for c in result["sources"]
    ]

    # console log for evaluation
    print("======= QUERY LOG =======")
    print("Q:", body.question)
    print("Chapter filter:", result["applied_chapter_filter"])
    print("Retrieval (ms):", result["retrieval_latency_ms"])
    print("Generation (ms):", result["generation_latency_ms"])
    for s in sources:
        print(f"- {s.chapter} p.{s.page} score={s.score:.3f}")
    print("=========================\n")

    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        retrieval_latency_ms=result["retrieval_latency_ms"],
        generation_latency_ms=result["generation_latency_ms"],
        applied_chapter_filter=result["applied_chapter_filter"],
    )
