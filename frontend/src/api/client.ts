import type { Analysis, Comment, Community, Post, User } from '../types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(detail.detail || 'Request failed')
  }
  return response.json() as Promise<T>
}

const mapUser = (user: any): User => ({ id: user.id, username: user.username, avatar: user.avatar, karma: user.karma, joinedAt: user.created_at })
const mapCommunity = (community: any): Community => ({ id: community.id, name: community.name, displayName: community.display_name, description: community.description, memberCount: community.member_count, accent: '#4d9b78', icon: community.display_name[0] })
const mapPost = (post: any): Post => ({ id: post.id, communityId: post.community_id, authorId: post.author_id, title: post.title, body: post.body, score: post.score, commentCount: post.comment_count, createdAt: post.created_at, flair: post.flair, image: post.image_url })
const mapComment = (comment: any): Comment => ({ id: comment.id, postId: comment.post_id, authorId: comment.author_id, parentCommentId: comment.parent_comment_id, body: comment.body, score: comment.score, createdAt: comment.created_at })

export const api = {
  users: async () => (await request<any[]>('/users')).map(mapUser),
  communities: async () => (await request<any[]>('/communities')).map(mapCommunity),
  posts: async () => (await request<any[]>('/posts')).map(mapPost),
  post: async (id: string) => mapPost(await request<any>(`/posts/${id}`)),
  comments: async (postId: string) => (await request<any[]>(`/posts/${postId}/comments`)).map(mapComment),
  discussion: (postId: string) => request(`/posts/${postId}/discussion`),
  search: async (query: string) => { const result = await request<any>(`/search?q=${encodeURIComponent(query)}`); return { posts: result.posts.map(mapPost), communities: result.communities.map(mapCommunity) } },
  createPost: async (payload: Pick<Post, 'communityId' | 'authorId' | 'title' | 'body'> & { flair?: string }) => mapPost(await request<any>('/posts', { method: 'POST', body: JSON.stringify({ community_id: payload.communityId, author_id: payload.authorId, title: payload.title, body: payload.body, flair: payload.flair }) })),
  createComment: async (postId: string, payload: { authorId: string; body: string; parentCommentId?: string | null }) => mapComment(await request<any>(`/posts/${postId}/comments`, { method: 'POST', body: JSON.stringify({ author_id: payload.authorId, body: payload.body, parent_comment_id: payload.parentCommentId || null }) })),
  votePost: (postId: string, userId: string, value: number) => request<{ score: number }>(`/posts/${postId}/vote`, { method: 'POST', body: JSON.stringify({ user_id: userId, value }) }),
  analyze: (postId: string) => request<Analysis>(`/posts/${postId}/analyze`, { method: 'POST' }),
}
