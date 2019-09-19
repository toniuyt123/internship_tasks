const triplets = (a) => {
  const lengths = new Set();
  const sides = {};
  
  for (let x = 1; x <= a; x++) {
    for (let y = x; y <= a; y++) {
      const dist = Math.sqrt(x * x + y * y);

      if (dist % 1 === 0) {
        sides[x] = y;
        lengths.add(dist);
      }
    }
  }

  return { lengths, sides };
};
const a = 4;
const canvasSize = 500;
const margin = 10;
const step = (canvasSize - margin * 2) / (a - 1);
let lengths, sides;

function setup() {

  const res = triplets(a);
  lengths = res.lengths;
  sides = res.sides;
  console.log(sides);
  
  createCanvas(canvasSize, canvasSize);
  strokeWeight(2);
}

function draw() {
  background(220);
  for (let x = margin; x <= canvasSize - margin; x += step) {
    for (let y = margin; y <= canvasSize - margin; y += step) {
      point(x, y);
       for (let x1 = margin; x1 <= canvasSize - margin; x1 += step) {
        for (let y1 = margin; y1 <= canvasSize - margin; y1 += step) {
          if (x !== x1 && y !== y1) {
            const c1 = Math.abs((y1 - y) / step) + 1;
            const c2 = Math.abs((x1 - x) / step) + 1;
            if (sides[c1] === c2 || sides[c2] === c1) {
              line(x, y, x1, y1);
            }
          }
        }
      }
    }
  }
}