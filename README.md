# Welcome! Добре дошли!
Hello, thanks for browsing this project! First of all, for those unfamiliar: CS50 is Harvard's Introduction to Computer Science.
It is the single most popular course on campus, with over 800 students taking it each semester. Professor David J. Mallan, the
person behind CS50, has "translated" the course through edX to CS50x - the online version of CS50, where people all around the
world can watch the course lectures and shorts (exercises), as well as do the assignments. Ultimately, the course culminates with
the final project whose criteria is to "build something of interest to you, that you solve an actual problem, that you impact your
community, or that you change the world. Strive to create something that outlives this course". This is how Anbuldict was born!

# ANBULDICT?
## ANcient BULgarian DICTionary
### Ancient Bulgarian
Bulgarian is a very old language, with its first manuscripts appearing since the 10th century, but also existing as a spoken
language since before Christ! Obviously, such an old language means that it has experienced many different periods and changes,
and the 10th century written form of Bulgarian is significantly different from the 21st century form. This brings to light the
need to translate the Bulgarian from different time periods - similarly to Ancient Greek differing greatly from Modern Greek.

### Existing solution and motivation for improvement
Thanks to Sofia University, there is a dictionary from Ancient Bulgarian to Bulgarian! However, it is indeed only one way. I.e.,
you would have to first search for a specific Ancient Bulgarian word and only then see its meaning in modern Bulgarian. This is
very useful to historians, but not so much to regular people that would like to check the meaning of a modern Bulgarian word in
Ancient Bulgarian (i.e., the other way around). <br />

This is especially relevant to me. One day, I might become an entrepreneur, starting
my own company. I still have no idea (or more like, I have many different ideas but nothing clearly formulated yet) what its main
activity would be; I do know that I want the company to be socially beneficial, though. The only other thing I know, is that I
would like to name it using an Ancient Bulgarian word. That would happen by first summarizing its activity in one (modern Bulgarian)
word and then translating this word to Ancient Bulgarian... so I hope you can see where I am going with this! <br />

This is why a dictionary TO (as opposed to FROM) Ancient Bulgarian would be extremely useful to me. For example, if my company's business is teaching people
how to achieve a healthy work/life balance and in general, a healthy lifestyle, I might summarize it in one word as "coach". The
Ancient Bulgarian word for coach is "каꙁател҄ь", transliterated to "kazatel"... so I got my company name (in this case)! Besides this,
I am sure that other people can benefit from Anbuldict as well - one possible use is tattoos! Lastly, I have also decided to add the
benefit of English to Ancient Bulgarian translation, to reach international audiences!

### More about Anbuldict as a system
So, now that its goal is clear, let's talk about using it: Anbuldict is available at anbuldict.herokuapp.com ... go visit it! I do
hope that its design should make it relatively intuitive. Nevertheless, here's most funcitionalities explained: <br />

(1) Homepage: a static welcome page <br />

(2) Search: regular search available through the navbar, allowing for a quick search of an English word (or part of one).
Additionally, there is an extended search functionality, available in a separate section. This extended functionality also allows the
use of (modern) Bulgarian as a search criteria, as well as other specifics, such as whether to look for a word containing the
search term, or an exact match. Ultimately, after a search is performed, if matching records are found in the database, a result
(or a few) shows up that can be clicked, leading to the... <br />

(3) Word page: a dynamic page, fillable with the word data. It starts with the word in Ancient Bulgarian, a button to add it
to favorites (working only for registered users), meanings in English and (modern) Bulgarian, and finishes with a link to its entry
in the Sofia University dictionary <br />

(4) User system: to allow for more complicated functionalities, a user system is implemented. Firstly, a user can register and
then subsequently log in. Then, they can suggest new words (to /hopefully/ be approved by the admin user). An on-screen keyboard is
provided, to allow entering Ancient Bulgarian characters. Users can also add and remove favorites, as explained in the previous
point. Additionally, they can delete a word they have proposed, by going to the word page described in point (3). If they
are the authors of this word indeed, then a "Delete" button will show up. Lastly, they can review all their suggestions in the
"My suggestions" section. Of course, user can also log out of the system. <br />

(4.1) Admin user: as explained, there is one user with more priviliges. They can directly add words (i.e., instead of suggestions)
and delete any word. They can also approve or reject suggestions by other users. <br />

### Even more technicalities
Anbuldict was built using the Flask framework, i.e., having Python as the backend, and, expectedly, HTML, CSS and JavaScript
on the frontend, with jinja as a templating engine. I have built the application practically from scratch, where I only borrowed
some code from the CS50's final assignment (assignment! so, not final project) - Finance, about handling logins. Everything on
the backend is programmed (i.e., no ready solutions), while for the front-end, I have made extensive use of the Bootstrap library. <br />

After finishing the work, I decided that I want to publish it. Doing some research showed that using Heroku was my best option.
This proved challenging, as we were not taught how to do it, but it was definitely doable with some googling. Perhaps even more problematic
was the fact that because of this I had to switch from using sqlite to Postresql, but I also managed to do this. <br />

Ultimately, I am very proud of the resulting product, as I see it as a fully functioning ecosystem. I have also extensively tested it, and tried to
break it as much as I can. I do not think it is perfect, as nothing can be; but I think it is very much foolproof, and common usage
(and hopefully, any usage, including from malicious users) should not lead to 500: Internal Server errors; there is as well
protection from SQL injections. Because of this, I believe that its general use can be extended. It would be especially helpful
to other people's CS50 final projects (do try to make as much as possible on your own, however!) so that they can build on top of
it. There's many generalizable functionalities, most notably - favorites and administration. As such, I have decided to open source
this project, available in github.com/s7oev/anbuldict_public !! Note that if you want to run it, you'd have to create a sqlite DB
yourself, or connect it to your personal Postresql database. If you do, here's a list of the database tables, and their respective
fields:

Users
- id
- username
- hash

Words
- id
- suhistdict
- bg
- en
- anbul
- addedby
- approved

Favorites
- favid
- userid
- wordid

Thank you... this was CS50x!