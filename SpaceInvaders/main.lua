local ENEMY_LEVEL_1=1
local ENEMY_LEVEL_2=2
local ENEMY_LEVEL_3=3
local GAME_STATE_PLAYING = 0
local GAME_STATE_GAME_LOST_SCREEN = 1
local GAME_STATE_GAME_WON_SCREEN = 2

local function make_coord(x, y)
    return {x = x, y = y}
end

local function descending_order(fst, snd)
    return fst > snd
end

local game_conf = {
    level_enemies = {
        {
            {kind=ENEMY_LEVEL_1, coord = make_coord(80,40)},
            {kind=ENEMY_LEVEL_1, coord = make_coord(160,60)},
            {kind=ENEMY_LEVEL_1, coord = make_coord(240,40)},
            {kind=ENEMY_LEVEL_1, coord = make_coord(320,60)},
            {kind=ENEMY_LEVEL_1, coord = make_coord(400,40)},
        },
        {
            {kind=ENEMY_LEVEL_2, coord = make_coord(80,40)},
            {kind=ENEMY_LEVEL_1, coord = make_coord(160,60)},
            {kind=ENEMY_LEVEL_2, coord = make_coord(240,40)},
            {kind=ENEMY_LEVEL_1, coord = make_coord(320,60)},
            {kind=ENEMY_LEVEL_2, coord = make_coord(400,40)},
        },
        {
            {kind=ENEMY_LEVEL_2, coord = make_coord(80,40)},
            {kind=ENEMY_LEVEL_2, coord = make_coord(160,60)},
            {kind=ENEMY_LEVEL_3, coord = make_coord(240,40)},
            {kind=ENEMY_LEVEL_2, coord = make_coord(320,60)},
            {kind=ENEMY_LEVEL_2, coord = make_coord(400,40)},
        },
        {
            {kind=ENEMY_LEVEL_3, coord = make_coord(80,40)},
            {kind=ENEMY_LEVEL_3, coord = make_coord(160,60)},
            {kind=ENEMY_LEVEL_3, coord = make_coord(240,40)},
            {kind=ENEMY_LEVEL_3, coord = make_coord(320,60)},
            {kind=ENEMY_LEVEL_3, coord = make_coord(400,40)},
        },

    },
    enemy_types = {
        [ENEMY_LEVEL_1] = {speed = 1, bullet_speed=4, size_coeff = 0.5},
        [ENEMY_LEVEL_2] = {speed = 1, bullet_speed=5, size_coeff = 0.4},
        [ENEMY_LEVEL_3] = {speed = 1, bullet_speed=6, size_coeff = 0.3}

    }
}

local function create_player()
    local player = {coord = {x = 100, y = 580}}
    function player:shoot(game_data)
        if self.bullets_generation_tick <= 0 then
            self.bullets_generation_tick = 30
            local bullet = {x = self.coord.x + 15, y = 520, h = 12, w = 4, velocity = -5}
            table.insert(game_data.bullets, bullet)
            love.audio.play(self.shoot_sound)
        end
    end
    function player:load()
        self.image = love.graphics.newImage('images/player.png')
        self.shoot_sound = love.audio.newSource('sounds/shoot.mp3','static')
        self.height = self.image:getHeight()
        self.width = self.image:getWidth() * 0.3
    end
    player.bullets_generation_tick = 30
    return player
end


local function create_enemy(description, game_data)
    local enemy_type = game_conf.enemy_types[description.kind]
    local height = game_data.enemy_img:getHeight() * enemy_type.size_coeff
    local width = game_data.enemy_img:getWidth() * enemy_type.size_coeff
    local enemy = {
        enemy_type = enemy_type, 
        coord = {x = description.coord.x, y = description.coord.y},
        height = height,
        width = width
    }

    return enemy
end

local function load_enemies_for_level(game_data, level)
    local enemies_to_create = game_conf.level_enemies[level]
    for _, enemy_template in ipairs(enemies_to_create) do
        local new_enemy = create_enemy(enemy_template, game_data)
        table.insert(game_data.enemies, new_enemy)
    end
end

local function level_transition(game_data)
    game_data.enemies = {}
    game_data.bullets = {}
    game_data.enemy_bullet_generation_tick = 150
    if game_data.current_level == nil then
        game_data.current_level = 1
    else
        game_data.current_level = game_data.current_level + 1
    end

    if game_data.current_level < table.getn(game_conf.level_enemies) + 1 then
        load_enemies_for_level(game_data, game_data.current_level)
    else
        game_data.game_state = GAME_STATE_GAME_WON_SCREEN
    end
end


local function get_object_center(object)
    return object.coord.x + object.width/2, object.coord.y + object.height/2
end

local function is_bullet_colliding_with_object(object, bullet)
    local x_mid = bullet.x + bullet.w/2
    local y_mid = bullet.y + bullet.h/2
    local x_mid_obj, y_mid_obj = get_object_center(object)
    local x_diff = math.abs(x_mid - x_mid_obj)
    local y_diff = math.abs(y_mid - y_mid_obj)
    if y_diff > object.height/2 + bullet.h/2 then
        return false
    end
    if x_diff > object.width/2  + bullet.w/2 then
        return false
    end
    return true
end


local function are_objects_colliding(fst, snd)
    local fst_mid_x, fst_mid_y = get_object_center(fst)
    local snd_mid_x, snd_mid_y = get_object_center(snd)
    local x_diff = math.abs(fst_mid_x - snd_mid_x)
    local y_diff = math.abs(fst_mid_y - snd_mid_y)
    if x_diff > fst.width/2 + snd.width/2 then
        return false
    end
    if y_diff > fst.height/2 + snd.height/2 then
        return false
    end
    return true
end

local game_data = {
    bullets = {},
    enemies = {},
    player = create_player(),
    enemy_img = nil,
    current_level = nil,
    game_state = GAME_STATE_PLAYING,
    enemy_bullet_generation_tick = 150
}

function love.load()
    game_data.player:load()
    music = love.audio.newSource('sounds/music.mp3','static')
    music:setLooping(true)
    love.audio.play(music)
    game_data.enemy_img = love.graphics.newImage('images/invader.png')
    game_data.enemy_shoot_sound = love.audio.newSource('sounds/shoot.mp3','static')
    math.randomseed(os.time())
    level_transition(game_data)
end

function love.draw()
    -- love.graphics.print("Space Invaders Example", 400, 300)
    love.graphics.setColor(1,1,1)
    if game_data.game_state == GAME_STATE_PLAYING then
        for _, bullet in ipairs(game_data.bullets) do
            love.graphics.rectangle("fill",bullet.x, bullet.y, bullet.w, bullet.h)
        end
        love.graphics.draw(game_data.player.image, game_data.player.coord.x, game_data.player.coord.y, 0, 0.3)
        for _, enemy in ipairs(game_data.enemies) do
            love.graphics.draw(game_data.enemy_img, enemy.coord.x, enemy.coord.y, 0, enemy.enemy_type.size_coeff)
        end
    elseif game_data.game_state == GAME_STATE_GAME_LOST_SCREEN then
        love.graphics.print("GAME OVER", 400, 300)
    elseif game_data.game_state == GAME_STATE_GAME_WON_SCREEN then
        love.graphics.print("VICTORY", 400, 300)
    end
end

local function handle_player_collision()
    local found_colliding = false
    for _, bullet in ipairs(game_data.bullets) do
        if bullet.velocity > 0 and is_bullet_colliding_with_object(game_data.player, bullet) then
            found_colliding = true
            break
        end
    end
    if not found_colliding then
        for _, enemy in ipairs(game_data.enemies) do
            if are_objects_colliding(enemy, game_data.player) then
                found_colliding = true
                break
            end
        end
    end
    if found_colliding then
        game_data.game_state = GAME_STATE_GAME_LOST_SCREEN
    end
end

local function handle_movement_of_enemies()
    local enemies_to_remove = {}
    for index, enemy in ipairs(game_data.enemies) do
        local speed = enemy.enemy_type.speed
        enemy.coord.y = enemy.coord.y + speed
        if enemy.coord.y > 600 then
            table.insert(enemies_to_remove, index)
        end
    end
    table.sort(enemies_to_remove, descending_order)
    for _, enemy_idx in ipairs(enemies_to_remove) do
         table.remove(game_data.enemies, enemy_idx)
    end
end

local function handle_collision_for_enemies()
    local enemies_to_remove = {}
    local bullets_to_remove = {}
    for enemy_idx, enemy in ipairs(game_data.enemies) do
        for i, bullet in ipairs(game_data.bullets) do
            if bullet.velocity < 0 and is_bullet_colliding_with_object(enemy, bullet) then
                table.insert(bullets_to_remove, i)
                table.insert(enemies_to_remove, enemy_idx)
            end
        end
    end
    table.sort(enemies_to_remove, descending_order)
    table.sort(bullets_to_remove, descending_order)
    for _, enemy_idx in ipairs(enemies_to_remove) do
        table.remove(game_data.enemies, enemy_idx)
    end
    for _, bullet_idx in ipairs(bullets_to_remove) do
        table.remove(game_data.bullets, bullet_idx)
    end
    if table.getn(game_data.enemies) == 0 then
        level_transition(game_data)
    end
end

local function handle_enemies_shoot()
    if game_data.enemy_bullet_generation_tick == 0 then
        game_data.enemy_bullet_generation_tick = 150
    else
        game_data.enemy_bullet_generation_tick = game_data.enemy_bullet_generation_tick - 1
        --print("Enemy shoot " .. game_data.enemy_bullet_generation_tick)
        return
    end
    local enemies_count = table.getn(game_data.enemies)
    local enemy_idx_to_shoot = math.random(enemies_count)
    local enemy = game_data.enemies[enemy_idx_to_shoot]
    local bullet = {
        x = enemy.coord.x + enemy.width/2 - 2,
        y = enemy.coord.y + enemy.height + 4,
        h = 12,
        w = 4,
        velocity = enemy.enemy_type.bullet_speed
    }
    table.insert(game_data.bullets, bullet)
    love.audio.play(game_data.enemy_shoot_sound)
end


function love.update()
    if love.keyboard.isDown('q') then
        love.event.quit()
    end
    if game_data.game_state ~= GAME_STATE_PLAYING then
        return
    end
    local player = game_data.player
    if love.keyboard.isDown('right') then
        if player.coord.x > 750 then
            player.coord.x = 750
        end
        player.coord.x = player.coord.x + 5
    end
    if love.keyboard.isDown('left') then
        if player.coord.x  < 10 then
            player.coord.x = 10
        end
        player.coord.x = player.coord.x - 5
    end
    if love.keyboard.isDown('space') then
        player:shoot(game_data)
    end
    local bullets_to_remove = {}
    for bullet_idx, bullet in ipairs(game_data.bullets) do
        bullet.y = bullet.y + bullet.velocity
        if bullet.y < 0 or bullet.y > 600 then
            table.insert(bullets_to_remove, bullet_idx)
        end
    end
    table.sort(bullets_to_remove, descending_order)
    for _, bullet_idx in ipairs(bullets_to_remove) do
        table.remove(game_data.bullets, bullet_idx)
    end
    handle_player_collision()
    handle_collision_for_enemies()
    handle_movement_of_enemies()
    handle_enemies_shoot()
    player.bullets_generation_tick = player.bullets_generation_tick - 1
end

