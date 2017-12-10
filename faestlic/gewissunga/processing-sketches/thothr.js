var step = 0.01;
var c = 0;
var p = 1.25

function setup() {
  createCanvas(800, 800);
  background(31);
}

function draw() {
  translate(width*0.48, height*0.48);
  for (var i = 0; i <= 5; i++) {
    var r = 350;
    var a1 = (p + (step*c))*PI
    var a2 = (p - (step*c))*PI

    if ((c*step) <= 0.5) {
      strokeWeight((c*step)*7);
    } else {
      strokeWeight((1-(c*step))*7);
    }
    stroke(255, 10);
    v1 = createVector(cos(a1)*r, sin(a1)*r);
    v2 = createVector(cos(a2)*r, sin(a2)*r);

    vectors = randomisePath(v1, v2);
    for (var a = 0; a < vectors.length - 1; a++) {
      line(vectors[a].x, vectors[a].y, vectors[a+1].x, vectors[a+1].y)
    }

    c += 1

    if ((c*step) >= 0.4) {
      c = 0;
      p += random()
    }
  }
}

function randomisePath(vector1, vector2) {
  var vectors = []
  vectors.push(vector2)

  for (var i = 0.1; i < 1; i += 0.1) {
    var x = (i * vector1.x) + ((1-i) * vector2.x);
    var y = (i * vector1.y) + ((1-i) * vector2.y)
    vectors.push(createVector(x,y));
  }

  vectors.push(vector1);

  vectors = vectors.map(function(x) {
    return createVector(x.x + randomGaussian(10,10), x.y + randomGaussian(10,10));
  });

  return vectors;

}
