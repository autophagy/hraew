var sigma = 10;
var beta = 8/3;
var rohm = 28;

var position;
var velocity;
var dt = 0.01;

var scaling = 14;

function setup() {
  createCanvas(800, 800);
  background(31);
  frameRate(30);
  position = createVector(1,0,0);
  velocity = createVector(0,0,0);
}

function draw() {
    translate(400, 400);
    for (var i = 1; i <= 50; i++) {
      velocity.x = sigma * (position.y - position.x);
      velocity.y = position.x * (rohm - position.z) - position.y;
      velocity.z = position.x * position.y - beta * position.z;

      velocity.mult(dt);
      var old_position = createVector(position.x, position.y);
      position.add(velocity);
      stroke(255, position.z/1.2);
      line(old_position.x * scaling, old_position.y * scaling, position.x * scaling, position.y * scaling);

    }
}