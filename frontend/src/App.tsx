import { useEffect, useState } from 'react'
import type { CSSProperties, ReactNode } from 'react'
import { Bell, Bookmark, ChevronDown, Compass, Feather, Home, Menu, MessageCircle, MoreHorizontal, Plus, Search, Share2, Sparkles, TrendingUp, UserRound, X } from 'lucide-react'
import { comments, communities, posts, users } from './data'
import { api } from './api/client'
import type { Analysis, Comment, Post, Vote } from './types'

const findUser = (id: string) => users.find((user) => user.id === id)!
const findCommunity = (id: string) => communities.find((community) => community.id === id)!
const formatCount = (value: number) => value > 999 ? `${(value / 1000).toFixed(value > 9999 ? 0 : 1)}k` : value.toString()

function Avatar({ label, accent = '#dce9e6' }: { label: string; accent?: string }) {
  return <span className="avatar" style={{ background: accent }}>{label}</span>
}

function VoteRail({ score, onVote }: { score: number; onVote: (vote: Vote) => void }) {
  const [vote, setVote] = useState<Vote>(null)
  const displayScore = score + (vote === 'up' ? 1 : vote === 'down' ? -1 : 0)
  const choose = (next: Vote) => { setVote(vote === next ? null : next); onVote(vote === next ? null : next) }
  return <div className="vote-rail"><button className={vote === 'up' ? 'vote active-up' : 'vote'} onClick={() => choose('up')} aria-label="Upvote">▲</button><strong>{formatCount(displayScore)}</strong><button className={vote === 'down' ? 'vote active-down' : 'vote'} onClick={() => choose('down')} aria-label="Downvote">▼</button></div>
}

function PostCard({ post, onOpen, onAnalyze, detail = false }: { post: Post; onOpen: () => void; onAnalyze?: () => void; detail?: boolean }) {
  const community = findCommunity(post.communityId)
  const author = findUser(post.authorId)
  const [analysis, setAnalysis] = useState(false)
  return <article className={detail ? 'post-card post-detail' : 'post-card'}>
    <div className="post-main">
      <VoteRail score={post.score} onVote={(vote) => api.votePost(post.id, 'u1', vote === 'up' ? 1 : vote === 'down' ? -1 : 0).catch(() => undefined)} />
      <div className="post-content">
        <div className="post-meta"><Avatar label={community.icon} accent={community.accent} /><button className="community-link">t/{community.name}</button><span>•</span><span>Posted by <button className="author-link">u/{author.username}</button></span><span>•</span><span>{post.createdAt}</span></div>
        <button className="post-title" onClick={onOpen}>{post.title}</button>
        {post.flair && <span className="flair">{post.flair}</span>}
        {post.body && <p className="post-body">{post.body}</p>}
        {post.image && <div className="post-image"><div className="image-swatch"><span>FIELD NOTES</span><b>A quieter web<br />starts here.</b></div></div>}
        <div className="post-actions"><button onClick={onOpen}><MessageCircle size={16} /> {post.commentCount} comments</button><button><Share2 size={16} /> Share</button><button><Bookmark size={16} /> Save</button><button onClick={() => { setAnalysis(!analysis); onAnalyze?.() }} className={analysis ? 'analyze active' : 'analyze'}><Sparkles size={16} /> {analysis ? 'Analyzing' : 'Analyze discussion'}</button><button aria-label="More"><MoreHorizontal size={18} /></button></div>
      </div>
    </div>
  </article>
}

function CommentItem({ comment, allComments, depth = 0 }: { comment: Comment; allComments: Comment[]; depth?: number }) {
  const author = findUser(comment.authorId)
  const replies = allComments.filter((item) => item.parentCommentId === comment.id)
  return <div className="comment-wrap" style={{ '--depth': Math.min(depth, 4) } as CSSProperties}><div className="comment-line"><Avatar label={author.avatar} /><div className="comment-body"><div className="comment-meta"><b>u/{author.username}</b><span>{comment.score} points</span><span>•</span><span>{comment.createdAt}</span></div><p>{comment.body}</p><div className="comment-actions"><button>↩ Reply</button><button>Share</button><button>More</button></div></div></div>{replies.map((reply) => <CommentItem key={reply.id} comment={reply} allComments={allComments} depth={depth + 1} />)}</div>
}

function Shell({ page, setPage, children, onSearch }: { page: string; setPage: (page: string) => void; children: ReactNode; onSearch: (query: string) => void }) {
  const [query, setQuery] = useState('')
  const nav = (next: string) => { setPage(next); window.scrollTo({ top: 0, behavior: 'smooth' }) }
  return <><header className="topbar"><div className="brand" onClick={() => nav('home')}><span className="brand-mark">t</span><span>threadline</span></div><div className="search-box"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && onSearch(query)} placeholder="Search Threadline" /><kbd>⌘ K</kbd></div><div className="top-actions"><button aria-label="Create post" onClick={() => nav('create')}><Plus size={20} /></button><button aria-label="Messages"><MessageCircle size={20} /></button><button aria-label="Notifications"><Bell size={20} /></button><button className="profile-chip" onClick={() => nav('profile')}><Avatar label="MC" accent="#d8e5df" /><ChevronDown size={15} /></button></div><button className="mobile-menu" aria-label="Open menu"><Menu /></button></header><div className="app-layout"><aside className="sidebar"><nav><button className={page === 'home' ? 'nav-item selected' : 'nav-item'} onClick={() => nav('home')}><Home size={18} /> Home</button><button className={page === 'popular' ? 'nav-item selected' : 'nav-item'} onClick={() => nav('popular')}><TrendingUp size={18} /> Popular</button><button className="nav-item" onClick={() => nav('community')}><Compass size={18} /> Explore</button></nav><div className="side-divider" /><p className="side-label">Your spaces</p>{communities.slice(0, 4).map((community) => <button className="community-nav" key={community.id} onClick={() => nav('community')}><Avatar label={community.icon} accent={community.accent} /><span>t/{community.name}</span></button>)}<button className="nav-item subdued" onClick={() => nav('create')}><Feather size={18} /> Create a post</button><div className="sidebar-footer">About&nbsp;&nbsp; • &nbsp;&nbsp;Rules&nbsp;&nbsp; • &nbsp;&nbsp;Privacy<br /><br />© 2025 Threadline</div></aside><main className="page-area">{children}</main></div></>
}

function HomePage({ onOpen, popular = false }: { onOpen: (id: string) => void; popular?: boolean }) {
  const visible = popular ? [...posts].sort((a, b) => b.score - a.score) : posts
  return <div className="content-grid"><section className="feed"><div className="page-heading"><div><p className="eyebrow">A community of communities</p><h1>{popular ? 'Popular discussions' : 'Good morning, Mira'}</h1><p className="heading-note">Thoughtful conversations worth your time.</p></div><button className="new-post" onClick={() => onOpen('create')}><Plus size={17} /> New post</button></div><div className="feed-tabs"><button className={!popular ? 'active' : ''}>Home</button><button className={popular ? 'active' : ''}>Popular</button><button>Recent</button><button className="sort"><ChevronDown size={15} /> Best</button></div>{visible.map((post) => <PostCard key={post.id} post={post} onOpen={() => onOpen(post.id)} />)}</section><aside className="right-rail"><section className="welcome-panel"><div className="panel-kicker">THREADLINE / 01</div><h2>Make room for a better conversation.</h2><p>Find perspectives, follow ideas, and keep the signal.</p><button onClick={() => onOpen('community')}>Explore communities <span>→</span></button></section><section className="trending-panel"><div className="panel-title"><b>Trending spaces</b><button onClick={() => onOpen('community')}>See all</button></div>{communities.slice(0, 3).map((community, index) => <button className="trending-item" key={community.id} onClick={() => onOpen('community')}><span className="rank">0{index + 1}</span><Avatar label={community.icon} accent={community.accent} /><span><b>t/{community.name}</b><small>{formatCount(community.memberCount)} members</small></span><span className="trend-arrow">↗</span></button>)}</section></aside></div>
}

function DetailPage({ postId, onBack }: { postId: string; onBack: () => void }) {
  const post = posts.find((item) => item.id === postId) || posts[0]
  const thread = comments.filter((comment) => comment.postId === post.id)
  const [analysis, setAnalysis] = useState<Analysis | null>(null); const [analyzing, setAnalyzing] = useState(false); const [analysisError, setAnalysisError] = useState('')
  const runAnalysis = async () => { setAnalyzing(true); setAnalysisError(''); try { setAnalysis(await api.analyze(post.id)) } catch (error) { setAnalysisError(error instanceof Error ? error.message : 'Analysis could not be completed') } finally { setAnalyzing(false) } }
  return <div className="detail-layout"><button className="back-link" onClick={onBack}>← Back to feed</button><PostCard post={post} onOpen={() => undefined} onAnalyze={runAnalysis} detail />{analyzing && <div className="analysis-panel analysis-loading"><Sparkles size={18} /><span>Reading the discussion and finding the signal...</span></div>}{analysisError && <div className="analysis-panel analysis-error"><b>Analysis unavailable</b><span>{analysisError}</span></div>}{analysis && <section className="analysis-panel"><div className="analysis-heading"><div><p className="eyebrow">Discussion analysis</p><h2>What this conversation is saying</h2></div><span className="analysis-badge">{analysis.overall_sentiment}</span></div><p className="analysis-summary">{analysis.summary}</p><div className="sentiment-row"><span><i className="positive-dot" /> Positive <b>{analysis.sentiment_percentages.positive}%</b></span><span><i className="neutral-dot" /> Neutral <b>{analysis.sentiment_percentages.neutral}%</b></span><span><i className="negative-dot" /> Negative <b>{analysis.sentiment_percentages.negative}%</b></span></div><div className="analysis-grid"><div className="analysis-section"><h3>Themes</h3><ul>{analysis.themes.map((t) => <li key={t}>{t}</li>)}</ul></div><div className="analysis-section"><h3>Viewpoints</h3><ul>{analysis.viewpoints.map((v) => <li key={v.name}><b>{v.name}</b>: {v.description} <span className="vp-sentiment">{v.sentiment_summary}</span></li>)}</ul></div><div className="analysis-section"><h3>Consensus</h3><p>{analysis.consensus || 'No clear consensus identified.'}</p></div><div className="analysis-section"><h3>Disagreements</h3><ul>{analysis.disagreements.map((d) => <li key={d}>{d}</li>)}</ul></div><div className="analysis-section"><h3>Arguments For</h3><ul>{analysis.arguments_for.map((a) => <li key={a.comment_id}>{a.text} <span className="arg-ref">(#{a.comment_id})</span></li>)}</ul></div><div className="analysis-section"><h3>Arguments Against</h3><ul>{analysis.arguments_against.map((a) => <li key={a.comment_id}>{a.text} <span className="arg-ref">(#{a.comment_id})</span></li>)}</ul></div><div className="analysis-section"><h3>Important Comments</h3><ul>{analysis.important_comments.map((ic) => <li key={ic.comment_id}><span className="imp-id">#{ic.comment_id}</span>: {ic.reason}</li>)}</ul></div><div className="analysis-section quality-metrics"><h3>Discussion Quality</h3><div className="metric-row"><span>Agreement</span><div className="metric-bar"><div className="metric-fill" style={{width: (analysis.discussion_quality.agreement_level*100)+'%'}}></div></div><span className="metric-value">{Math.round(analysis.discussion_quality.agreement_level*100)}%</span></div><div className="metric-row"><span>Disagreement</span><div className="metric-bar"><div className="metric-fill" style={{width: (analysis.discussion_quality.disagreement_level*100)+'%'}}></div></div><span className="metric-value">{Math.round(analysis.discussion_quality.disagreement_level*100)}%</span></div><div className="metric-row"><span>Polarization</span><div className="metric-bar"><div className="metric-fill" style={{width: (analysis.discussion_quality.polarization*100)+'%'}}></div></div><span className="metric-value">{Math.round(analysis.discussion_quality.polarization*100)}%</span></div><div className="metric-row"><span>Substantive</span><div className="metric-bar"><div className="metric-fill" style={{width: (analysis.discussion_quality.substantive_discussion*100)+'%'}}></div></div><span className="metric-value">{Math.round(analysis.discussion_quality.substantive_discussion*100)}%</span></div></div></div><small className="analysis-footnote">{analysis.comments_analyzed} comments analyzed · {analysis.ai_provider}</small></section>}<div className="discussion-header"><h2>{post.commentCount} comments</h2><button className="sort"><ChevronDown size={15} /> Best</button></div><div className="comment-editor"><Avatar label="MC" /><input placeholder="Join the conversation..." /></div><div className="comments">{thread.filter((comment) => !comment.parentCommentId).map((comment) => <CommentItem key={comment.id} comment={comment} allComments={thread} />)}</div></div>
}

function CommunityPage({ onOpen }: { onOpen: (id: string) => void }) {
  const community = communities[0]
  return <div className="community-page"><div className="community-hero" style={{ '--accent': community.accent } as CSSProperties}><div className="community-avatar">{community.icon}</div><div><p className="eyebrow">Threadline community</p><h1>t/{community.name}</h1><p>{community.description}</p></div><button className="join-button">Join</button></div><div className="community-stats"><span><b>{formatCount(community.memberCount)}</b> members</span><span><b>2.4k</b> online</span><span>Created Mar 12, 2018</span></div><div className="feed-tabs"><button className="active">Popular</button><button>Recent</button><button>Top</button></div>{posts.filter((post) => post.communityId === community.id).map((post) => <PostCard key={post.id} post={post} onOpen={() => onOpen(post.id)} />)}</div>
}

function SearchPage({ query, onOpen }: { query: string; onOpen: (id: string) => void }) {
  const [results, setResults] = useState<Post[]>([])
  useEffect(() => { api.search(query).then((response) => setResults(response.posts)).catch(() => setResults([])) }, [query])
  return <div className="search-page"><p className="eyebrow">Search results</p><h1>Results for “{query || 'everything'}”</h1><div className="search-tabs"><button className="active">Posts <span>{results.length}</span></button><button>Communities</button><button>People</button></div>{results.length ? results.map((post) => <PostCard key={post.id} post={post} onOpen={() => onOpen(post.id)} />) : <div className="empty-state"><Search size={30} /><h2>Nothing surfaced yet</h2><p>Try a broader phrase or explore a community.</p></div>}</div>
}

function ProfilePage({ onOpen }: { onOpen: (id: string) => void }) {
  const user = users[0]
  return <div className="profile-page"><div className="profile-header"><Avatar label={user.avatar} accent="#d8e5df" /><div><p className="eyebrow">Member profile</p><h1>u/{user.username}</h1><p>Building small things with care. Usually found near a good question.</p><div className="profile-stats"><span><b>{formatCount(user.karma)}</b> karma</span><span><b>4y</b> on Threadline</span></div></div><button className="outline-button">Edit profile</button></div><div className="feed-tabs"><button className="active">Posts</button><button>Comments</button><button>Saved</button></div>{posts.filter((post) => post.authorId === user.id).map((post) => <PostCard key={post.id} post={post} onOpen={() => onOpen(post.id)} />)}</div>
}

function CreatePage({ onPublish }: { onPublish: (title: string, body: string, communityId: string) => Promise<void> }) {
  const [title, setTitle] = useState(''); const [body, setBody] = useState(''); const [communityId, setCommunityId] = useState(communities[0]?.id || ''); const [error, setError] = useState('')
  const submit = async () => { try { await onPublish(title, body, communityId) } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Could not publish post') } }
  return <div className="create-page"><p className="eyebrow">Share something</p><h1>Create a post</h1><p className="heading-note">Start a thread that gives people something to think about.</p><div className="create-form"><select value={communityId} onChange={(event) => setCommunityId(event.target.value)}>{communities.map((community) => <option key={community.id} value={community.id}>t/{community.name}</option>)}</select><input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="A clear, specific title" /><textarea value={body} onChange={(event) => setBody(event.target.value)} placeholder="What would you like to share?" rows={9} /><div className="form-row"><button className="attach-button"><Plus size={17} /> Add image</button><select defaultValue="Discussion"><option>Discussion</option><option>Question</option><option>Showcase</option></select></div>{error && <p className="form-error">{error}</p>}<div className="form-actions"><button className="draft-button">Save draft</button><button className="publish-button" onClick={submit}>Publish post</button></div></div></div>
}

export default function App() {
  const [page, setPage] = useState('home')
  const [selectedPost, setSelectedPost] = useState('p1')
  const [query, setQuery] = useState('')
  const [, setDataVersion] = useState(0)
  useEffect(() => { Promise.all([api.users(), api.communities(), api.posts()]).then(([nextUsers, nextCommunities, nextPosts]) => { users.splice(0, users.length, ...nextUsers); communities.splice(0, communities.length, ...nextCommunities); posts.splice(0, posts.length, ...nextPosts); setDataVersion((version) => version + 1) }).catch(() => undefined) }, [])
  useEffect(() => { if (page === 'detail') api.comments(selectedPost).then((nextComments) => { comments.splice(0, comments.length, ...nextComments); setDataVersion((version) => version + 1) }).catch(() => undefined) }, [page, selectedPost])
  const open = (target: string) => { if (target.startsWith('p')) { setSelectedPost(target); setPage('detail') } else if (target === 'create' || target === 'community' || target === 'profile' || target === 'popular') setPage(target); else setPage('home') }
  const content = page === 'detail' ? <DetailPage postId={selectedPost} onBack={() => setPage('home')} /> : page === 'community' ? <CommunityPage onOpen={open} /> : page === 'profile' ? <ProfilePage onOpen={open} /> : page === 'create' ? <CreatePage onPublish={async (title, body, communityId) => { const created = await api.createPost({ title, body, communityId, authorId: 'u1' }); posts.unshift(created); setPage('home') }} /> : page === 'search' ? <SearchPage query={query} onOpen={open} /> : <HomePage onOpen={open} popular={page === 'popular'} />
  return <Shell page={page} setPage={setPage} onSearch={(value) => { setQuery(value); setPage('search') }}>{content}</Shell>
}
