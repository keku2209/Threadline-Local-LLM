export type Vote = 'up' | 'down' | null

export interface User {
  id: string
  username: string
  avatar: string
  karma: number
  joinedAt: string
}

export interface Community {
  id: string
  name: string
  displayName: string
  description: string
  memberCount: number
  accent: string
  icon: string
}

export interface Post {
  id: string
  communityId: string
  authorId: string
  title: string
  body: string
  score: number
  commentCount: number
  createdAt: string
  flair?: string
  image?: string
}

export interface Comment {
  id: string
  postId: string
  authorId: string
  parentCommentId: string | null
  body: string
  score: number
  createdAt: string
}

export interface Analysis {
  post_id: string
  summary: string
  overall_sentiment: string
  sentiment_counts: { positive: number; negative: number; neutral: number }
  sentiment_percentages: { positive: number; negative: number; neutral: number }
  themes: string[]
  viewpoints: Array<{ name: string; description: string; comment_ids: string[]; sentiment_summary: string }>
  consensus: string
  disagreements: string[]
  arguments_for: Array<{ text: string; comment_id: string; supporting_ids: string[] }>
  arguments_against: Array<{ text: string; comment_id: string; supporting_ids: string[] }>
  important_comments: Array<{ comment_id: string; reason: string }>
  discussion_quality: { agreement_level: number; disagreement_level: number; polarization: number; substantive_discussion: number }
  comments_analyzed: number
  ai_provider: string
}
