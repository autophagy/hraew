var layers = []

function setup() {
  createCanvas(600, 600);
  background(31);

  for (var i = 0; i < 8; i++) {
    layers[i] = new LunarLayer(15*i + 80, 100 + (i*40), random(1000));
    layers[i].quicken();
  }
  frameRate(30);
}

function draw() {
  background(31);
  for (var x = 0; x < layers.length; x++) {
    layers[x].advance();
    layers[x].draw();
  } 

  strokeWeight(200);
  fill(0,0);
  stroke(31);
  ellipse(width/2, height/2, 800, 800);
}


// Lunar Layer
function LunarLayer(colour, yOffset, seedValue) {
  this.colour = colour;
  this.yOffset = yOffset
  this.seedValue = seedValue

  this.progress = 0;
  this.inc = 0.005;

  this.amp = 200;
  this.xspacing = 1;

  this.points = [];

  this.quicken = function() {
    noiseSeed(this.seedValue);
    for (var x = 0; x<= width; x+= this.xspacing) {
      this.points.push(noise(this.progress)*this.amp+this.yOffset);
      this.progress += this.inc;
    }
  }

  this.advance = function() {
    this.points.shift();
    noiseSeed(this.seedValue);
    this.points.push(noise(this.progress)*this.amp+this.yOffset);
    this.progress += this.inc;
  }
  
  this.draw = function() {
    stroke(this.colour, 255);
    strokeWeight(1);
    fill(this.colour, 200);
    beginShape();
    vertex(0, height);
    for (var a = 0; a < this.points.length; a++) {
      vertex(a * this.xspacing, this.points[a]);
    }
    vertex(width, height);
    endShape();
    }
  }
