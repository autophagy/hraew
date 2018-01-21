function setup() {
  createCanvas(800, 800);
  background(31);
}

function draw() {
  translate(width*0.48, height*0.48);
  for(var a = 0; a < 5; a++) {
    var r = 350;

    var a1 = randomGaussian(0.5,PI/4)
    var a2 = a1 + randomGaussian(0, PI/3)

    stroke(255, 15);
    v1 = createVector(cos(a1)*r, sin(a1)*r);
    v2 = createVector(cos(a2)*r, sin(a2)*r);

    var vectors = randomisePath(v1, v2);
    for (var i = 0; i < vectors.length - 1; i++) {
      line(vectors[i].x, vectors[i].y, vectors[i+1].x, vectors[i+1].y)
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