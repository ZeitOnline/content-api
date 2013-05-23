#Content-API

ZEIT ONLINE content API - A [flask](http://flask.pocoo.org/) –
[Solr](http://lucene.apache.org/solr/) middleware


##Frequent questions

###What is this?
This is the ZEIT ONLINE content API project as available at
http://developer.zeit.de. It enables you to access articles and corresponding
metadata from the ZEIT newspaper archive, as well as recent articles from ZEIT
and ZEIT ONLINE.

###Is it ready?
It is still in public beta. We are working on improving the quality of our data
as well as the stability of our code. You are welcome to test and experiment
with the API, take a look at the code, file a bug report or request a feature.

###Where are the docs?
You can find the documentation at our developer portal over at
http://developer.zeit.de

###Can I run the API locally?
Yes. It is tailored to the infrastructure we have here at ZEIT ONLINE, though.
So it might not be of too much use for other scenarios and will require some
adaptation. See below for instructions.

###How can I get in touch?
We would love to hear your ideas and feedback. Join the discussion in the
[issues section](http://github.com/ZeitOnline/content-api/issues), contact us
on Twitter at [zeitonline_dev](http://twitter.com/zeitonline_dev) or send an
Email to [api@zeit.de](mailto:api@zeit.de).


##Getting started

Check out the repository, change to the project folder and then bootstrap the
project like this:

    $ python bootstrap.py

Now run buildout with the development configuration:

    $ bin/buildout -c dev.cfg

This will install dependencies, generate executables for the API, the developer
portal and the testsuite and download a Solr package. To start the Solr
locally, switch to parts/solr-server and enter:

    $ java -jar start.jar

With the search server running, you can now start the testsuite:

    $ bin/tests