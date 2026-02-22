with open('Home.py', 'r', encoding='utf-8') as f:
    content = f.read()

MARKER_START = '# Animated background: canvas particles + floating orbs'
MARKER_END = '""", unsafe_allow_html=True)\n\n\ndef detect_column_types'

i1 = content.find(MARKER_START)
i2 = content.find('""", unsafe_allow_html=True)', i1)
end_of_block = i2 + len('""", unsafe_allow_html=True)')

print(f"Block found: {i1} -> {end_of_block}")
print("Tail of block:", repr(content[end_of_block-5:end_of_block+5]))

NEW_BLOCK = '''# Animated background: deep-space particles + shooting stars + orbs
st.markdown("""
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
<canvas id="bg-canvas"></canvas>
<script>
(function() {
    var canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    function rand(min, max) { return Math.random() * (max - min) + min; }

    // ---- Mouse ----
    var mouse = { x: -9999, y: -9999 };
    window.addEventListener('mousemove', function(e) { mouse.x = e.clientX; mouse.y = e.clientY; });
    window.addEventListener('mouseleave', function() { mouse.x = -9999; mouse.y = -9999; });

    // ---- Color palette (accent blue, purple, cyan, green) ----
    var PALETTE = [
        [41,151,255],
        [191,90,242],
        [100,210,255],
        [48,209,88],
        [255,159,10],
    ];

    // ---- Regular particles ----
    var NUM = 90;
    var particles = [];
    for (var i = 0; i < NUM; i++) {
        var c = PALETTE[Math.floor(Math.random() * PALETTE.length)];
        particles.push({
            x: rand(0, window.innerWidth),
            y: rand(0, window.innerHeight),
            vx: rand(-0.3, 0.3),
            vy: rand(-0.3, 0.3),
            r: rand(1.2, 3.0),
            cr: c[0], cg: c[1], cb: c[2],
            alpha: rand(0.4, 1.0),
            pulseSpeed: rand(0.01, 0.03),
            pulseOffset: rand(0, Math.PI * 2),
        });
    }

    // ---- Shooting stars ----
    var stars = [];
    function spawnStar() {
        var c = PALETTE[Math.floor(Math.random() * PALETTE.length)];
        var angle = rand(-0.3, 0.3) + Math.PI * 0.25; // mostly top-right direction
        var speed = rand(8, 18);
        stars.push({
            x: rand(0, window.innerWidth),
            y: rand(0, window.innerHeight * 0.5),
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            len: rand(60, 160),
            life: 1.0,
            decay: rand(0.012, 0.025),
            cr: c[0], cg: c[1], cb: c[2],
        });
    }
    // Spawn initial stars
    for (var s = 0; s < 3; s++) spawnStar();

    // ---- Ripple on click ----
    var ripples = [];
    window.addEventListener('click', function(e) {
        ripples.push({ x: e.clientX, y: e.clientY, r: 0, life: 1.0 });
    });

    var frame = 0;

    function draw() {
        frame++;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Spawn a new shooting star every ~120 frames
        if (frame % 120 === 0) spawnStar();

        // ---- Draw shooting stars ----
        for (var s = stars.length - 1; s >= 0; s--) {
            var st = stars[s];
            var grad = ctx.createLinearGradient(
                st.x, st.y,
                st.x - st.vx * (st.len / 10),
                st.y - st.vy * (st.len / 10)
            );
            grad.addColorStop(0, 'rgba(' + st.cr + ',' + st.cg + ',' + st.cb + ',' + st.life * 0.9 + ')');
            grad.addColorStop(1, 'rgba(' + st.cr + ',' + st.cg + ',' + st.cb + ',0)');
            ctx.beginPath();
            ctx.moveTo(st.x, st.y);
            ctx.lineTo(st.x - st.vx * (st.len / 10), st.y - st.vy * (st.len / 10));
            ctx.strokeStyle = grad;
            ctx.lineWidth = 1.5 * st.life;
            ctx.stroke();

            // Tiny glowing head
            ctx.beginPath();
            ctx.arc(st.x, st.y, 2 * st.life, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(' + st.cr + ',' + st.cg + ',' + st.cb + ',' + st.life + ')';
            ctx.fill();

            st.x += st.vx;
            st.y += st.vy;
            st.life -= st.decay;
            if (st.life <= 0) stars.splice(s, 1);
        }

        // ---- Draw ripples ----
        for (var ri = ripples.length - 1; ri >= 0; ri--) {
            var rp = ripples[ri];
            ctx.beginPath();
            ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(41,151,255,' + rp.life * 0.5 + ')';
            ctx.lineWidth = 1.5;
            ctx.stroke();
            rp.r += 4;
            rp.life -= 0.03;
            if (rp.life <= 0) ripples.splice(ri, 1);
        }

        // ---- Draw particle connections ----
        var MAX_DIST = 150;
        var MOUSE_DIST = 200;
        for (var i = 0; i < particles.length; i++) {
            var p = particles[i];
            // Pulse alpha
            var pulse = Math.sin(frame * p.pulseSpeed + p.pulseOffset) * 0.25 + 0.75;
            var a = p.alpha * pulse;

            // Particle-to-particle lines
            for (var j = i + 1; j < particles.length; j++) {
                var q = particles[j];
                var dx = p.x - q.x, dy = p.y - q.y;
                var dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < MAX_DIST) {
                    var lineAlpha = (1 - dist / MAX_DIST) * 0.2 * pulse;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(q.x, q.y);
                    ctx.strokeStyle = 'rgba(' + p.cr + ',' + p.cg + ',' + p.cb + ',' + lineAlpha + ')';
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }

            // Mouse connection + repel
            var mdx = mouse.x - p.x, mdy = mouse.y - p.y;
            var mdist = Math.sqrt(mdx*mdx + mdy*mdy);
            if (mdist < MOUSE_DIST) {
                // Draw line to cursor
                var mAlpha = (1 - mdist / MOUSE_DIST) * 0.45;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.strokeStyle = 'rgba(' + p.cr + ',' + p.cg + ',' + p.cb + ',' + mAlpha + ')';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // Gentle repel force
                var force = (1 - mdist / MOUSE_DIST) * 0.5;
                p.vx -= (mdx / mdist) * force * 0.05;
                p.vy -= (mdy / mdist) * force * 0.05;
            }

            // Speed cap
            var speed = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
            if (speed > 1.2) { p.vx *= 0.95; p.vy *= 0.95; }
            if (speed < 0.1) { p.vx += rand(-0.05, 0.05); p.vy += rand(-0.05, 0.05); }

            // Draw particle with glow
            var glow = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 3);
            glow.addColorStop(0, 'rgba(' + p.cr + ',' + p.cg + ',' + p.cb + ',' + a + ')');
            glow.addColorStop(0.4, 'rgba(' + p.cr + ',' + p.cg + ',' + p.cb + ',' + a * 0.3 + ')');
            glow.addColorStop(1, 'rgba(' + p.cr + ',' + p.cg + ',' + p.cb + ',0)');
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * 3, 0, Math.PI * 2);
            ctx.fillStyle = glow;
            ctx.fill();

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(' + p.cr + ',' + p.cg + ',' + p.cb + ',' + a + ')';
            ctx.fill();

            // Move
            p.x += p.vx;
            p.y += p.vy;

            // Wrap around edges (instead of bounce - smoother feel)
            if (p.x < -10) p.x = canvas.width + 10;
            if (p.x > canvas.width + 10) p.x = -10;
            if (p.y < -10) p.y = canvas.height + 10;
            if (p.y > canvas.height + 10) p.y = -10;
        }

        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
""", unsafe_allow_html=True)'''

content = content[:i1] + NEW_BLOCK + content[end_of_block:]

with open('Home.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
