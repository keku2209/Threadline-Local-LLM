from datetime import datetime, timedelta

from .database import Base, SessionLocal, engine
from .models import Comment, Community, Post, User

USERS = [
    ('u1', 'mira.codes', 'Mira Chen', 'MC', 18420), ('u2', 'orbiting', 'Owen Reed', 'OR', 9320), ('u3', 'nathaniel_w', 'Nathan Williams', 'NW', 7210),
    ('u4', 'slowly_then', 'Sam Taylor', 'ST', 4580), ('u5', 'pixel_forge', 'Priya Shah', 'PF', 12300), ('u6', 'green_tea_dev', 'Grace Tan', 'GT', 2840),
    ('u7', 'the_real_jules', 'Jules Martin', 'TJ', 6140), ('u8', 'analog_sunrise', 'Ana Silva', 'AS', 1970), ('u9', 'civic_signal', 'Civic Signal', 'CS', 8700), ('u10', 'marble_fox', 'Max Fox', 'MF', 3320),
]
COMMUNITIES = [
    ('c1', 'technology', 'Technology', 'The place for thoughtful conversations about the tools shaping tomorrow.', 1840000),
    ('c2', 'design', 'Design', 'A community for sharing work, process, and ideas across the design world.', 632000),
    ('c3', 'books', 'Books', 'A quiet corner for readers, writers, and people who keep one more book nearby.', 918000),
    ('c4', 'climate', 'Climate', 'Evidence-led discussion about our changing planet and what we can do about it.', 245000),
    ('c5', 'learnprogramming', 'Learn Programming', 'A welcoming place to ask questions and share your programming journey.', 1200000),
]
TOPICS = [
    ('Should AI be allowed in college assignments?', 'u1', 'c1', 'The useful question may not be whether students use AI, but whether they can explain and take responsibility for the work it helps produce.'),
    ('Is remote work better than office work?', 'u2', 'c1', 'After four years of hybrid work, I am curious which parts people would keep and which would they gladly leave behind.'),
    ('Are smartphones making students less productive?', 'u3', 'c1', 'The answer feels more complicated than simply turning notifications off. What has actually worked for you?'),
    ('What makes a design system last beyond its first team?', 'u5', 'c2', 'The best systems seem to be social agreements as much as collections of components.'),
    ('Show me a book that changed your mind', 'u7', 'c3', 'Not necessarily a favorite. I am looking for books that rearranged the furniture in your head.'),
    ('What does a genuinely useful critique sound like?', 'u4', 'c2', 'The best feedback I have received was specific enough to act on and generous enough to hear.'),
    ('How should cities make space for shade?', 'u9', 'c4', 'Small interventions add up, especially in neighborhoods where heat is felt most intensely.'),
    ('The case for reading one book very slowly', 'u10', 'c3', 'A reading habit that survives a busy year might have less to do with discipline than with removing the pressure to finish.'),
    ('What are you learning the long way?', 'u6', 'c5', 'Some concepts only settle after we have tried, failed, and returned to them with better questions.'),
    ('The quiet joy of maintaining old software', 'u1', 'c5', 'There is a particular satisfaction in making a small, dependable tool a little kinder to its next user.'),
    ('Can public transit be designed around trust?', 'u9', 'c4', 'Reliable information can be as important as reliable service when people decide how to move through a city.'),
    ('Which creative habit survives a bad week?', 'u8', 'c2', 'I am collecting practices that are small enough to keep when energy and time are both scarce.'),
    ('What should beginners stop worrying about?', 'u6', 'c5', 'Every field has a few anxieties that feel essential at first and turn out to be mostly noise.'),
    ('A defense of the annotated margin', 'u3', 'c3', 'Notes in books are not a performance. They are a record of one mind meeting another.'),
    ('What gives you hope about climate work?', 'u5', 'c4', 'Looking for concrete stories, projects, and local changes that make the future feel less abstract.'),
]

SUPPORT = ['I think the useful distinction is intention. Tools can extend learning when the person still understands the result.', 'There is a real risk of outsourcing the struggle that makes the idea stick. Convenience is not always the same as progress.', 'A limited-use policy with transparent disclosure seems more honest than pretending the tools are not already here.']
REMOTE_WORK_COMMENTS = [
    'Remote work gives me longer stretches of focused time and removes the daily commute, so I can organize my day around the work that needs concentration.',
    'I miss the quick conversations that happen in an office. Remote teams can coordinate well, but it takes more deliberate communication and newer coworkers may feel isolated.',
    'A hybrid schedule works best for me: remote days for focused tasks and shared office days for planning and collaboration. The right balance depends on the team and the work.',
]
REMOTE_WORK_REPLIES = [
    'The extra focus is real. Regular check-ins also help people feel connected and make it easier to ask a quick question.',
    'Agreed. A predictable overlap day can restore some spontaneous collaboration without requiring everyone to commute daily.',
    'That split makes sense to me; teams should choose office time for work that benefits from being together.',
]
REMOTE_WORK_DEEP_REPLY = 'Clear expectations about availability and intentional in-person time matter more than requiring everyone to be in the office by default.'
AI_ASSIGNMENT_COMMENTS = [
    'Using AI to brainstorm is helpful when I still write the final answer myself.',
    'Having AI write an assignment is dishonest and harms students’ learning.',
    'Some professors allow AI for outlines but prohibit it in final submissions.',
]
AI_ASSIGNMENT_REPLIES = [
    'Clear rules make it easier for students to use AI responsibly.',
    'Relying on AI for every answer is a bad way to learn.',
    'A disclosure statement could show when AI helped with an assignment.',
]
AI_ASSIGNMENT_DEEP_REPLY = 'What matters is whether each student can explain the reasoning behind the submitted work.'
SMARTPHONE_COMMENTS = [
    'Notifications constantly interrupt me, and I get much less studying done.',
    'Putting my phone away during study blocks helped me focus and finish assignments faster.',
    'Late-night scrolling leaves me tired and makes it harder to pay attention in class.',
]
SMARTPHONE_REPLIES = [
    'A scheduled check-in break is easier for me to stick to than checking every alert.',
    'Do Not Disturb works well; I still let calls from family come through.',
    'The phone is useful for calendars and research, but social apps are a distraction during class.',
]
SMARTPHONE_DEEP_REPLY = 'When I keep it on the desk, I reach for it without noticing and lose my train of thought.'


def seed():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        db.add_all([User(id=i, username=u, display_name=d, avatar=a, karma=k, created_at=now - timedelta(days=500 + n * 100)) for n, (i, u, d, a, k) in enumerate(USERS)])
        db.add_all([Community(id=i, name=n, display_name=d, description=desc, member_count=count, created_at=now - timedelta(days=900)) for i, n, d, desc, count in COMMUNITIES])
        for index, (title, author_id, community_id, body) in enumerate(TOPICS, 1):
            discussion_data = {
                1: (AI_ASSIGNMENT_COMMENTS, AI_ASSIGNMENT_REPLIES, AI_ASSIGNMENT_DEEP_REPLY),
                2: (REMOTE_WORK_COMMENTS, REMOTE_WORK_REPLIES, REMOTE_WORK_DEEP_REPLY),
                3: (SMARTPHONE_COMMENTS, SMARTPHONE_REPLIES, SMARTPHONE_DEEP_REPLY),
            }
            support_comments, replies, deep_reply = discussion_data.get(
                index,
                (SUPPORT, ['This is where I land too, although the tradeoff changes depending on the context.'] * len(SUPPORT), 'The disagreement is useful because it makes the assumptions visible.'),
            )
            post = Post(id=f'p{index}', community_id=community_id, author_id=author_id, title=title, body=body, score=3000 - index * 113, comment_count=5, flair='Discussion', created_at=now - timedelta(hours=index * 3))
            db.add(post)
            for comment_index, text in enumerate(support_comments):
                comment_id = f'cm{index}_{comment_index}'
                comment = Comment(id=comment_id, post_id=post.id, author_id=USERS[(index + comment_index) % len(USERS)][0], body=text, score=180 - comment_index * 37, created_at=now - timedelta(hours=index * 2, minutes=comment_index * 8))
                db.add(comment)
                db.add(Comment(id=f'cm{index}_{comment_index}_r', post_id=post.id, author_id=USERS[(index + comment_index + 4) % len(USERS)][0], parent_comment_id=comment_id, body=replies[comment_index], score=42 + comment_index * 11, created_at=now - timedelta(hours=index, minutes=comment_index * 5)))
            db.add(Comment(id=f'cm{index}_deep', post_id=post.id, author_id='u10', parent_comment_id=f'cm{index}_1_r', body=deep_reply, score=19, created_at=now - timedelta(minutes=index * 4)))
        db.commit()
        print(f'Seeded {len(USERS)} users, {len(COMMUNITIES)} communities, {len(TOPICS)} posts, and nested comment trees.')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
