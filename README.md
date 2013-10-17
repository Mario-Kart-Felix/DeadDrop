Dead Drop
=========

In a nutshell
-------------

> A dead drop is a method of espionage tradecraft used to pass items between two individuals using a secret location.


This is a very simple implementation of the dead drop mechanism that uses telephony as a method of communication and facial recognition for authentication. The application is written in Python + Flask, is hosted on an Ubuntu AWS EC2 instance, and utilizes Twilio and SkyBiometry APIs to do most of the heavy lifting.

Try it!
-------

Call 510-587-9562 (the secret phone number shared by the agents) and follow the prompts to leave a secret message. You will be describing the facial characteristics of the receiving agent, something that was presumably agreed upon in advance. With the drop complete, it is time to impersonate a second agent and retrieve the message.

Visit [Dead Drop Access Panel](http://ec2-54-200-89-154.us-west-2.compute.amazonaws.com/deaddrop) and provide the URL of the agent's face. You could take a picture of your own face and upload it somewhere public or cheat and use Google Images to find a suitable face. If that fits the recipient's profile, you will be provided a secret code. Call 510-587-9562 back and enter the code to listen to the secret message.

Well done, agent!

What's the point?
-----------------

I have been immersed in the Microsoft ecosystem for the majority of my career. To be sure, Visual Studio + .NET is a fantastic combination. However, I have always been drawn to the "other side." Whether reading Hacker News, working through the Django tutorial, or kicking the tires on the latest Ubuntu distro, I enjoy learning and expanding my horizons. Writing this application allowed me to practice Python, learn Flask and get some first-hand experience with setting up an AWS instance.

The idea actually started out as a Shazam clone, where the user would call a phone number, play a song fragment into the handset and receive a text message with song information, no installed app necessary! Having completed 90% of the coding, I discovered that the documentation for the acoustic fingerprinting API (Echoprint) was in fact incorrect and did not support over-the-air music fragments as was claimed. No luck with the alternative Gracenote API either.

The next iteration focused on making more use of the Twilio interface - texting a photo of oneself to unlock a secret message. Facial recognition API from SkyBiometry worked well. Sending an SMS with an attached photo - not so much, as Twilio does not yet support attached media from regular/long numbers. Had to regroup yet again, finally landing on the current solution.

Lessons learned
---------------

System configuration presented the steepest learning curve and proved to be much more challenging than learning a new language, framework or API. Configuring Ubuntu, Apache and AWS probably consumed about 50% of the total effort.

**Ubuntu:** Linux has certainly come a long way since I first tried Red Hat Linux more than ten years ago. The Unity UI is similar enough to Windows to make for a smooth transition. I've been running Ubuntu in VirtualBox at home for some time now, however I did get to spend more time with the console during development. Why doesn't Windows have an apt-get equivalent??

**Apache:** This one turned out to be particularly difficult, as every obstacle I ran into seemed to invite a multitude of different solutions and felt very much like trial-and-error. Just getting the web app to recognize an environment variable turned into a 2-hour adventure. Having used Apache in the past with VentureTap (also open-sourced), I don't recall running into many issues. Perhaps that's the difference between shared hosting and installing and configuring Apache + mod_wsgi from scratch.

**Amazon Web Services:** The AWS dashboard looked intimidating, but actually setting up an EC2 instance was a piece of cake. Really looking forward to trying more of their offerings.

**Python:** Very nice, very readable language. I first used it years ago to test drive the original incarnation of the Google App Engine, and have been looking for an excuse to use it since. The code ended up being pretty simple (the only generator expression got refactored out) and I never felt constrained by the language. Eclipse, on the other hand, felt very clunky as compared to Visual Studio.

**Flask:** Having gone through the official Django tutorial and very much digging what it has to offer, it was not the right fit for this application. I needed something much lighter and Flask fit the bill perfectly. Routing was dead simple and the limitations of the Twilio interface forced me to write a web page using Jinja templating, which was a good experience overall. For a large application with fairly common functionality, Django would still be the go-to technology, however Flask works better for APIs and small, custom web applications.

**Data storage:** As much as I'm curious about SQLAlchemy, I decided to save myself the trouble of setting up a relational data store and opted to store the profile + message in a binary file on disk. *This is definitely not thread-safe*, but was a reasonable trade-off given the simplicity of this exercise.

**Twilio:** A great API for interacting with phone and SMS infrastructure programmatically. The documentation is fantastic and possibilities are many. Implementing the survey-like workflow over the phone did not feel natural with the TwiML responses and required some creative coding to minimize code bloat. Lack of support for media attachments on regular phone numbers was disappointing, but I'm certain this will be rectified in the near future.

**SkyBiometry:** This cloud-based face detection and recognition API was trivial to integrate with and did its work surprisingly well. It is not 100% on the mark (especially when determining the subject's mood), however the results are consistent and performance satisfactory. The [Dead Drop Access Panel](http://ec2-54-200-89-154.us-west-2.compute.amazonaws.com/deaddrop) page is worth visiting just for trying out this interface.
