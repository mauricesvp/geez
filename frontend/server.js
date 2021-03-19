'use strict';

const express = require('express');
const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const path = require('path');

const PORT = 8080;
const HOST = '0.0.0.0';

mongoose.connect('mongodb://mongodb/geezdb',
    {
        useNewUrlParser: true,
        useUnifiedTopology: true
    }
);
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', function callback () {
            console.log('Conntected To Mongo Database');
});

var topicSchema = Schema(
    {
        id: Number,
        author: String,
        category: String,
        date: Number,
        post: String,
        first_changed: Number,
        title: String,
        latest_author_comment: String,
        latest_comment: Number
    },
    {
        collection: "tickets"
    }
);

var Topic = db.model("Topic", topicSchema, "topics");

async function findTopics() {
    var topics = await Topic.find({}).lean().exec();
    return topics;
}

const app = express();
app.use(express.static(__dirname));
app.set('view engine', 'ejs');
app.disable('x-powered-by');

app.use(function (req, res, next) {
    res.setHeader(
        'Content-Security-Policy',
        "default-src 'self' 'unsafe-inline' cdn.datatables.net cdnjs.cloudflare.com;"
    );
    next();

});

app.get('/', async function (req, res) {
    await findTopics()
        .then(topics => {
            topics.forEach((topic, index) => topics[index].latest_comment = new Date(topic.date*1000).toLocaleString());
            res.render("index", {topics: topics})
        })
        .catch(err => {
            res.render("index", {topics: {}})
        });
});

app.get('/robots.txt', (req, res) => {
  res.sendFile(path.join(__dirname + '/robots.txt'));
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);
