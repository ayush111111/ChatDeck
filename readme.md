Build both export paths into your app:

POST /add_card → always saves to DB

POST /send_to_notion → for Notion integration (easy + automatic)

GET /anki_deck → for .apkg download (Anki users)



TODO

add dspy
- make llm based code modular


improve UI

add a cap to the conversation / find a way to deal with large conversations


add pdf support - I am the user for it - I frequently need to summarise books into anki cards
- varying number of cards
- density of information
- type of card - quiz / fill in the blank / thorough (dense)
- wasnt the "core" purpose summarising chats though - i use it more for books than chats

- to summarise files, the app will need a frontend or a sidebar to upload files

Priority

- anki connection - syncing without desktop app is not possible - try with the app
- book to flashcard - algorithm and logic - will need time and iterations
- - v1 - the design pattern book (410 pages - try set of algorithms, images, core "22" patterns + solid + oop = ~30 "concepts" - 2-3 flashcards per pattern and 1 for for the rest = ~70 cards)
    - density of information
    - "golden" card set from anki

there are better interfaces out there - so just focus on getting the algorithm right for you



https://augmentingcognition.com/ltm.html
> Research Paper -> anki deck

> Image -> anki deck: I have an Anki question which simply says: “Visualize the graph Jones 2011 made of the probability curves for physicists making their prizewinning discoveries by age 30 and 40”. The answer is the image shown above, and I count myself as successful if my mental image is roughly along those lines.

> making Anki cards is an act of understanding in itself - shared decks and deck creation apps are fill-ins until you make your own deck
> Avoid the yes/no pattern
> Using Anki for APIs, books, videos, seminars, conversations, the web, events, and places: Nearly everything I said earlier about Ankifying papers applies also to other resources. Here's a few tips. I've separated out the discussion for APIs into an appendix, which you can read below, if interested.

> For seminars and conversations with colleagues I find it surprisingly helpful to set Anki quotas. For instance, for seminars I try to find at least three high-quality questions to Ankify. For extended conversations, at least one high-quality question to Ankify. I've found that setting quotas helps me pay more attention, especially during seminars. (I find it much easier a priori to pay attention in one-on-one conversation.)

> I'm more haphazard about videos, events, and places. It'd be good to, say, systematically Ankify 3-5 questions after going on an outing or to a new restaurant, to help me remember the experience. I do this sometimes. But I haven't been that systematic.

> I tend to Ankify in real time as I read papers and books. For seminars, conversations, and so on I prefer to immerse myself in the experience. Instead of getting out Anki, I will quickly make a mental (or paper) note of what I want to Ankify. I then enter it into Anki later. This requires some discipline; it's one reason I prefer to set a small quota, so that I merely have to enter a few questions later, rather than dozens.

> What determines the steepness of the curve, i.e., how quickly memories decay? In fact, the steepness depends on many things. For instance, it may be steeper for more complex or less familiar concepts. You may find it easier to remember a name that sounds similar to names you've heard before: say, Richard Hamilton, rather than Suzuki Harunobu. So they'd have a shallower curve. Similarly, you may find it easier to remember something visual than verbal. Or something verbal rather than a motor skill. And if you use more elaborate ways of remembering – mnemonics, for instance, or just taking care to connect an idea to other things you already know – you may be able to flatten the curve out** Although this expansion is much studied, there is surprisingly little work building detailed predictive models of the expansion. An exception is: Burr Settles and Brendan Meeder, A Trainable Spaced Repetition Model for Language Learning (2016). This paper builds a regression model to predict the decay rate of student memory on Duolingo, the online language learning platform. The result was not only better prediction of decay rates, but also improved Duolingo student engagement..

https://jesungpark.com/blog/spaced-repetition.html
History of spaced repetition algorithms
