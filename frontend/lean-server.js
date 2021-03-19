'use strict';

const express = require('express');
const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const path = require('path');

const PORT = 8080;
const HOST = '0.0.0.0';

const app = express();
app.use(express.static(__dirname));
app.set('view engine', 'ejs');

app.get('/', function (req, res) {
    res.render("index", {topics: {}})
});

app.get('/robots.txt', (req, res) => {
  res.sendFile(path.join(__dirname + '/robots.txt'));
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);
