import type { Comment, Community, Post, User } from './types'

export const users: User[] = [
  { id: 'u1', username: 'mira.codes', avatar: 'MC', karma: 18420, joinedAt: '2020-03-18' },
  { id: 'u2', username: 'orbiting', avatar: 'OR', karma: 9320, joinedAt: '2021-07-02' },
  { id: 'u3', username: 'nathaniel_w', avatar: 'NW', karma: 7210, joinedAt: '2019-11-11' },
  { id: 'u4', username: 'slowly_then', avatar: 'ST', karma: 4580, joinedAt: '2022-01-24' },
  { id: 'u5', username: 'pixel_forge', avatar: 'PF', karma: 12300, joinedAt: '2018-06-10' },
  { id: 'u6', username: 'green_tea_dev', avatar: 'GT', karma: 2840, joinedAt: '2023-04-16' },
  { id: 'u7', username: 'the_real_jules', avatar: 'TJ', karma: 6140, joinedAt: '2020-09-08' },
  { id: 'u8', username: 'analog_sunrise', avatar: 'AS', karma: 1970, joinedAt: '2024-02-20' },
  { id: 'u9', username: 'civic_signal', avatar: 'CS', karma: 8700, joinedAt: '2021-12-05' },
  { id: 'u10', username: 'marble_fox', avatar: 'MF', karma: 3320, joinedAt: '2022-08-30' },
]

export const communities: Community[] = [
  { id: 'c1', name: 'technology', displayName: 'Technology', description: 'The place for thoughtful conversations about the tools shaping tomorrow.', memberCount: 1840000, accent: '#ef6a45', icon: 'T' },
  { id: 'c2', name: 'design', displayName: 'Design', description: 'A community for sharing work, process, and ideas across the design world.', memberCount: 632000, accent: '#9b7bdb', icon: 'D' },
  { id: 'c3', name: 'books', displayName: 'Books', description: 'A quiet corner for readers, writers, and people who keep one more book nearby.', memberCount: 918000, accent: '#d69a37', icon: 'B' },
  { id: 'c4', name: 'climate', displayName: 'Climate', description: 'Evidence-led discussion about our changing planet and what we can do about it.', memberCount: 245000, accent: '#4d9b78', icon: 'C' },
  { id: 'c5', name: 'learnprogramming', displayName: 'Learn Programming', description: 'A welcoming place to ask questions and share your programming journey.', memberCount: 1200000, accent: '#427fa9', icon: 'L' },
]

export const posts: Post[] = [
  { id: 'p1', communityId: 'c1', authorId: 'u1', title: 'What is a piece of technology you quietly use every single day?', body: 'Not the flashy new launch. I mean the small, dependable tools that have earned a permanent place in your routine. Mine is a tiny command-line script that turns a messy folder into a tidy archive.', score: 2841, commentCount: 486, createdAt: '2h ago', flair: 'Discussion' },
  { id: 'p2', communityId: 'c2', authorId: 'u5', title: 'I redesigned my personal site around one idea: less, but better', body: 'After years of adding case studies, animations, and clever interactions, I removed almost everything. The result feels more like me, and the work is easier to find.', score: 1420, commentCount: 128, createdAt: '5h ago', flair: 'Process', image: 'studio' },
  { id: 'p3', communityId: 'c3', authorId: 'u3', title: 'The books that changed how you see other people', body: '', score: 978, commentCount: 213, createdAt: '7h ago' },
  { id: 'p4', communityId: 'c4', authorId: 'u9', title: 'A hopeful climate story from my city: our river is coming back', body: 'The restoration project passed its five-year mark this week. Fish counts are up, the old industrial lots are becoming wetlands, and the public river walk is full every weekend.', score: 3260, commentCount: 304, createdAt: '9h ago', flair: 'Good News' },
  { id: 'p5', communityId: 'c5', authorId: 'u6', title: 'I finally understand recursion, and it was not the explanation I expected', body: 'The breakthrough came when I stopped thinking of recursion as a function calling itself and started thinking about the smaller version of the same problem.', score: 742, commentCount: 89, createdAt: '11h ago', flair: 'Learning' },
  { id: 'p6', communityId: 'c1', authorId: 'u2', title: 'The web is getting faster, but my attention is getting slower', body: 'A few notes after switching off almost all notifications for a month.', score: 621, commentCount: 76, createdAt: '14h ago' },
  { id: 'p7', communityId: 'c2', authorId: 'u7', title: 'Show me the most useful design critique you have ever received', body: '', score: 553, commentCount: 61, createdAt: '1d ago' },
  { id: 'p8', communityId: 'c3', authorId: 'u10', title: 'A reading habit that actually survived a busy year', body: 'I stopped setting page goals and started leaving books in places where I naturally pause.', score: 489, commentCount: 42, createdAt: '1d ago' },
]

export const comments: Comment[] = [
  { id: 'cm1', postId: 'p1', authorId: 'u2', parentCommentId: null, body: 'A good text editor. It is the first thing I open and the one tool I trust to still be there in ten years.', score: 621, createdAt: '1h ago' },
  { id: 'cm2', postId: 'p1', authorId: 'u4', parentCommentId: 'cm1', body: 'Same. There is something comforting about a tool that does not ask you to become a different person to use it.', score: 188, createdAt: '48m ago' },
  { id: 'cm3', postId: 'p1', authorId: 'u1', parentCommentId: 'cm2', body: 'That is exactly it. The best tools feel like an extension of your hands, not another place to perform.', score: 93, createdAt: '34m ago' },
  { id: 'cm4', postId: 'p1', authorId: 'u8', parentCommentId: 'cm1', body: 'I would add the humble clipboard manager to this list.', score: 77, createdAt: '26m ago' },
  { id: 'cm5', postId: 'p1', authorId: 'u9', parentCommentId: null, body: 'Public transit apps. Imperfect, but being able to see the system breathe in real time has changed how I move through my city.', score: 304, createdAt: '1h ago' },
  { id: 'cm6', postId: 'p1', authorId: 'u5', parentCommentId: 'cm5', body: 'The live delay alerts have saved me more times than I want to admit.', score: 41, createdAt: '18m ago' },
  { id: 'cm7', postId: 'p2', authorId: 'u3', parentCommentId: null, body: 'The restraint is doing a lot of work here. The work still feels rich because the hierarchy is so clear.', score: 210, createdAt: '3h ago' },
  { id: 'cm8', postId: 'p2', authorId: 'u5', parentCommentId: 'cm7', body: 'Thank you. That was the part I was most nervous about removing.', score: 52, createdAt: '2h ago' },
]
