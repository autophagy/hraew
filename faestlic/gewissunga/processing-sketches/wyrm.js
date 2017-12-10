var velocity;
var offset;

function setup() {
  velocity = createVector(0.01, 0.01);
  offset = createVector(0.0, 50.0);
  createCanvas(800, 800);
  background(31);
  frameRate(30);
}

function draw() {
  var location = createVector(noise(offset.x)*(width/1.2), noise(offset.y)*height);

  offset.add(velocity);

  var tval = map(location.x, 0, width/2, 15, 30);
  stroke(225, 30);
  fill(0, 0);
  var radius = map(location.x, 0, width/2, 0, 60);
  ellipse(location.x, location.y, radius, radius);
  ellipse(width-location.x, location.y, radius, radius);
}