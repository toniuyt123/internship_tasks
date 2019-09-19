const fs = require('fs');
const path = require('path');

const express = require('express')
const app = express()
const port = 3000

const triplets = (a) => {
  const lengths = new Set();
  lengths.add(0);

  for (let x = 1; x <= a; x++) {
    for (let y = x; y <= a; y++) {
      const dist = Math.sqrt(x * x + y * y);

      if (dist % 1 === 0) {
        lengths.add(Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2)));
      }
    }
  }

  return lengths;
};

let sides;

app.use(express.urlencoded())
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/', (req, res) => {
  const a = req.body.A;

  if (a < 0 || a >= 20000) {
    res.redirect('/');
  }

  sides = triplets(a);

  console.log(Math.max(...sides), sides.size - 1);
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))