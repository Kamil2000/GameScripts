
var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
        }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

function makeCoord(x, y) {
    return {x, y}
}

var levels = [
    {
        platforms: [makeCoord(600, 400), makeCoord(50, 250), makeCoord(750, 220)],
        player: makeCoord(100, 145),
        door: makeCoord(750, 175),
        bombs: [makeCoord(300, 16)]
    },
    {
        platforms: [makeCoord(360, 300), makeCoord(0, 150), makeCoord(750, 150), makeCoord(750, 450)],
        player: makeCoord(100, 340),
        door: makeCoord(750, 105),
        bombs: [makeCoord(300, 16), makeCoord(600, 16)]
    },
];

var gameParams = {
    gameOver: false,
    score: 0,
    level: -1,
    loadNewLevel: true,
    colliders: []
};

var game = new Phaser.Game(config);

function preload () {
    this.load.image('sky', 'assets/sky.png');
    this.load.image('ground', 'assets/platform.png');
    this.load.image('star', 'assets/star.png');
    this.load.image('bomb', 'assets/bomb.png');
    this.load.svg('door', 'assets/door.svg', {width:60, height:100});
    this.load.spritesheet('dude', 'assets/dude.png', { frameWidth: 32, frameHeight: 48 });
}

function create() {
    gameParams.sky = this.add.image(400, 300, 'sky');
    gameParams.cursors = this.input.keyboard.createCursorKeys();
    this.anims.create({
        key: 'left',
        frames: this.anims.generateFrameNumbers('dude', { start: 0, end: 3 }),
        frameRate: 10,
        repeat: -1
    });

    this.anims.create({
        key: 'turn',
        frames: [ { key: 'dude', frame: 4 } ],
        frameRate: 20
    });

    this.anims.create({
        key: 'right',
        frames: this.anims.generateFrameNumbers('dude', { start: 5, end: 8 }),
        frameRate: 10,
        repeat: -1
    });
}

function deleteLevel() {
    gameParams.platforms.clear(true, true);
    gameParams.platforms.destroy(true);
    gameParams.platforms = null;
    gameParams.stars.clear(true, true);
    gameParams.stars.destroy(true);
    gameParams.start = null;
    gameParams.bombs.clear(true, true);
    gameParams.bombs.destroy();
    gameParams.doors.clear(true, true);
    gameParams.doors.destroy();
    gameParams.scoreText.destroy();
    var collider;
    for(collider of gameParams.colliders) {
        collider.destroy()
    }
    gameParams.colliders = []
}

function handleAdvanceLevel() {
    if(! gameParams.loadNewLevel) {
        return;
    }
    if (gameParams.level >= levels.length) {
        return;
    }
    gameParams.loadNewLevel = false;
    gameParams.level++;
    if(gameParams.level != 0) {
        deleteLevel.bind(this)();
    }
    if (gameParams.level === levels.length) {
        this.add.text(200, 200, "Victory!!!", { fontSize: '32px', fill: '#000' });
        gameParams.player.destroy();
        this.anims.destroy(true);
        gameParams.player = null;
        return;
    }
    createLevel.bind(this)(gameParams.level);
}

function advanceLevel() {
    gameParams.loadNewLevel = true;
}

function createLevel(levelIdx) {
    console.log("Level " + levelIdx + "\n");
    var levelProperties = levels[levelIdx]

    var platforms = this.physics.add.staticGroup();

    platforms.create(400, 568, 'ground').setScale(2).refreshBody();

    var platformCoord;
    for(platformCoord of levelProperties.platforms) {
        platforms.create(platformCoord.x, platformCoord.y, 'ground')
    }

    gameParams.platforms = platforms;
    var player;
    if(levelIdx === 0) {
        player = this.physics.add.sprite(levelProperties.player.x, levelProperties.player.y, 'dude');
        player.setBounce(0.2);
        player.setCollideWorldBounds(true);
        gameParams.player = player;
    } else {
        player = gameParams.player;
        player.x = levelProperties.player.x;
        player.y = levelProperties.player.y;
    }

    gameParams.stars = this.physics.add.group({
        key: 'star',
        repeat: 10,
        setXY: { x: 12, y: 0, stepX: 70 }
    });

    gameParams.stars.children.iterate(function (child) {
        child.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));
    });

    var doors = this.physics.add.staticGroup();
    gameParams.doors = doors;
    doors.create(levelProperties.door.x, levelProperties.door.y, 'door');

    gameParams.bombs = this.physics.add.group();
    var bombCoord;
    for(bombCoord of levelProperties.bombs) {
        var bomb = gameParams.bombs.create(bombCoord.x, bombCoord.y, 'bomb');
        bomb.setBounce(1);
        bomb.setCollideWorldBounds(true);
        bomb.setVelocity(Phaser.Math.Between(-200, 200), 20);
        bomb.allowGravity = false;
    }
    gameParams.scoreText = this.add.text(16, 16, 'score: ' + str(gameParams.score), { fontSize: '32px', fill: '#000' });
    gameParams.colliders.push(this.physics.add.collider(player, doors, (player, door) => {advanceLevel();}, null, this))
    gameParams.colliders.push(this.physics.add.collider(player, platforms));
    gameParams.colliders.push(this.physics.add.collider(gameParams.stars, platforms));
    gameParams.colliders.push(this.physics.add.collider(gameParams.bombs, platforms));
    gameParams.colliders.push(this.physics.add.overlap(player, gameParams.stars, collectStar, null, this));
    gameParams.colliders.push(this.physics.add.collider(player, gameParams.bombs, hitBomb, null, this));
}

function update () {
    handleAdvanceLevel.bind(this)();
    if (gameParams.gameOver) {
        return;
    }
    if (gameParams.player == null) {
        return;
    }
    if (gameParams.cursors.left.isDown) {
        gameParams.player.setVelocityX(-160);

        gameParams.player.anims.play('left', true);
    } else if (gameParams.cursors.right.isDown) {
        gameParams.player.setVelocityX(160);

        gameParams.player.anims.play('right', true);
    } else {
        gameParams.player.setVelocityX(0);
        gameParams.player.anims.play('turn');
    }
    if (gameParams.cursors.up.isDown && gameParams.player.body.touching.down) {
        gameParams.player.setVelocityY(-330);
    }
}

function collectStar (player, star) {
    star.disableBody(true, true);

    //  Add and update the score
    gameParams.score += 10;
    gameParams.scoreText.setText('Score: ' + gameParams.score);

    if (gameParams.stars.countActive(true) === 0)
    {
        //  A new batch of stars to collect
        gameParams.stars.children.iterate(function (child) {
            child.enableBody(true, child.x, 0, true, true);
        });
        var x = (player.x < 400) ? Phaser.Math.Between(400, 800) : Phaser.Math.Between(0, 400);
    }
}

function hitBomb (player, bomb) {
    this.physics.pause();
    player.setTint(0xff0000);
    player.anims.play('turn');
    gameParams.gameOver = true;
    this.add.text(200, 200, "Defeat!!!", { fontSize: '32px', fill: '#000' });
}
