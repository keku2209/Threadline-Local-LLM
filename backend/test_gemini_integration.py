import os
import sys
from pathlib import Path

# Ensure UTF-8 encoding output for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=" * 70)
print("GEMINI INTEGRATION AND FALLBACK TEST")
print("=" * 70)

# TEST A: Gemini Available
print("\n[TEST A] Testing POST /api/posts/p1/analyze with Gemini API enabled...")
resp_a = client.post('/api/posts/p1/analyze')
data_a = resp_a.json()

print(f"    ✓ HTTP Status: {resp_a.status_code}")
assert resp_a.status_code == 200, "Expected 200 OK"

required_fields = [
    'post_id', 'summary', 'overall_sentiment', 'sentiment_counts',
    'sentiment_percentages', 'themes', 'viewpoints', 'consensus',
    'disagreements', 'arguments_for', 'arguments_against',
    'important_comments', 'discussion_quality', 'comments_analyzed', 'ai_provider'
]

print("    ✓ Checking response schema...")
for field in required_fields:
    assert field in data_a, f"Missing field: {field}"

print(f"    ✓ AI Provider reported: {data_a['ai_provider']}")
assert 'fallback' not in data_a['ai_provider'].lower(), f"Expected real Gemini provider, got fallback: {data_a['ai_provider']}"
assert 'gemini' in data_a['ai_provider'].lower(), f"Expected Gemini provider, got: {data_a['ai_provider']}"

print(f"    ✓ Summary generated ({len(data_a['summary'])} chars): {data_a['summary'][:80]}...")
print(f"    ✓ Overall Sentiment: {data_a['overall_sentiment']}")
print(f"    ✓ Sentiment counts: {data_a['sentiment_counts']}")
print(f"    ✓ Viewpoints extracted: {len(data_a['viewpoints'])} viewpoints")
assert len(data_a['viewpoints']) > 0, "Expected at least one extracted viewpoint from Gemini"
for vp in data_a['viewpoints']:
    print(f"        - Viewpoint: {vp['name']} (Supported by comment IDs: {vp['comment_ids']})")
    assert len(vp['comment_ids']) > 0, f"Expected non-empty comment_ids for viewpoint {vp['name']}"

print(f"    ✓ Consensus: {data_a['consensus']}")
print(f"    ✓ Disagreements: {len(data_a['disagreements'])} items")
print(f"    ✓ Arguments For: {len(data_a['arguments_for'])} items")
print(f"    ✓ Arguments Against: {len(data_a['arguments_against'])} items")
assert len(data_a['arguments_for']) > 0 or len(data_a['arguments_against']) > 0, "Expected extracted arguments from Gemini"

print(f"    ✓ Important Comments: {len(data_a['important_comments'])} items")
assert len(data_a['important_comments']) > 0, "Expected extracted important comments from Gemini"
print(f"    ✓ Discussion Quality: {data_a['discussion_quality']}")


# TEST B: Multi-Discussion Semantic Differentiation (p1 vs p2)
print("\n[TEST B] Testing POST /api/posts/p2/analyze to compare against p1...")
resp_p2 = client.post('/api/posts/p2/analyze')
data_p2 = resp_p2.json()

print(f"    ✓ HTTP Status: {resp_p2.status_code}")
assert resp_p2.status_code == 200, "Expected 200 OK for p2"
print(f"    ✓ AI Provider reported for p2: {data_p2['ai_provider']}")
assert 'fallback' not in data_p2['ai_provider'].lower(), f"Expected real Gemini provider for p2, got: {data_p2['ai_provider']}"

print(f"    ✓ p1 Summary: {data_a['summary'][:70]}...")
print(f"    ✓ p2 Summary: {data_p2['summary'][:70]}...")
assert data_a['summary'] != data_p2['summary'], "p1 and p2 summaries should be substantially different"
assert data_a['themes'] != data_p2['themes'], "p1 and p2 themes should be substantially different"
print("    ✓ Verified p1 and p2 semantic analyses produce distinct results!")


# TEST C: Gemini Unavailable -> Local Fallback
print("\n[TEST C] Testing POST /api/posts/p1/analyze with Gemini disabled (Fallback Mode)...")
original_key = os.environ.get('GEMINI_API_KEY')
try:
    os.environ['GEMINI_API_KEY'] = ''
    resp_c = client.post('/api/posts/p1/analyze')
    data_c = resp_c.json()

    print(f"    ✓ HTTP Status: {resp_c.status_code}")
    assert resp_c.status_code == 200, "Expected 200 OK in fallback mode"

    for field in required_fields:
        assert field in data_c, f"Fallback missing field: {field}"

    print(f"    ✓ AI Provider reported: {data_c['ai_provider']}")
    assert 'fallback' in data_c['ai_provider'].lower(), f"Expected fallback provider, got: {data_c['ai_provider']}"
    print(f"    ✓ Fallback Summary: {data_c['summary'][:80]}...")
    print(f"    ✓ Fallback Sentiment: {data_c['overall_sentiment']} ({data_c['sentiment_counts']})")
    print(f"    ✓ Fallback Discussion Quality: {data_c['discussion_quality']}")

finally:
    if original_key:
        os.environ['GEMINI_API_KEY'] = original_key

print("\n" + "=" * 70)
print("ALL GEMINI INTEGRATION & FALLBACK TESTS PASSED SUCCESSFULLY! ✓")
print("=" * 70)

