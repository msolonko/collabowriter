from project import db

from project.db_models import Prompt

db.session.add(Prompt(prompt="If you had a superpower, which one would you have?"))

db.session.add(Prompt(prompt="How would you describe your favorite color to a color blind person?"))

db.session.add(Prompt(prompt="How would you solve world hunger?"))

db.session.add(Prompt(prompt="Describe an innovative way to use a pencil."))

db.session.add(Prompt(prompt="How would you sell someone a pen?"))

db.session.add(Prompt(prompt="What would you do with 1 billion dollars?"))

db.session.add(Prompt(prompt="Write a new pledge of allegiance to the United States"))

db.session.add(Prompt(prompt="Propose 10 alternate ways of making a decision besides flipping a coin"))

db.session.add(Prompt(prompt="Would you want to increase your IQ by 50 points? Why or why not?"))

db.session.add(Prompt(prompt="Propose and defend a ridiculous dessert combination"))

db.session.commit()