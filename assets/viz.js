(function(){
    Math.seedrandom('5'); //2, 5*

    var width = 1920,
            height = 1080

    var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height)
            .call(d3.behavior.zoom().on("zoom", function () {
                svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
                }))
            .append("g");

    var force = d3.layout.force()
            .size([width, height]);

    d3.json('assets/elclasico2017.json', function(error, json) {
        if (error) throw error;

        var i = 0;

        var last_player = false;

        while (!last_player) {
            last_player = (json.nodes[i].type == "account");
            i++;
        }

        var counts = json.nodes.slice(0, --i).map((n) => n.count);

        var max_count = Math.max(...counts)
        var min_count = Math.min(...counts)

        force
                .nodes(json.nodes)
                .links(json.links)
                .start();

        //Filtering nodes without links
        force.nodes( 
            force.nodes()
                 .filter((d) => { return d.weight > 0;}) 
            );


        force.gravity(0.2);

        force.linkDistance(height/4);

        force.charge(function(node) {
            if (node.type === 'player-rm' || node.type === 'player-bcn') return -1210; 
            return -853; 
        });        

        // -1000, -30
        // -1000, -500
        // -500, -1000
        // -1000, -1000 <---------------
        // -890, -850
        // -1200, -850 <----------------
        // -1200, -860 <----------------
        // -1200, -855 <----------------
        // -1200, -853 <----------------
        // -1210, -853 <----------------
        // -1215, -853 <----------------
        
        force.start();

        var link = svg.selectAll(".link")
                .data(force.links())
                .enter().append("line")
                .attr("class", "link")
                .style("stroke", (d) => { 
                    switch(d.type) {
                        case "rm":
                            return "#0E0A99";
                        case "bcn":
                            return "#850404";
                        default:
                            return "#000000";
                    } 
            });

        var node = svg.selectAll(".node")
                .data(force.nodes())
                .enter().append("g")
                .attr("class", "node")
                .call(force.drag);

        //https://gist.github.com/aaizemberg/78bd3dade9593896a59d
        function custom_colors(n) {
          var colors = ["#ff9900", "#109618", "#BE62BE", "#dd4477", "#66aa00",
             "#1CCF95", "#22aa99", "#aaaa11", "#D9E806", "#e67300", "#651067", 
             "#329262", "#5574a6", "#D9067E"];            
          return colors[n % colors.length];
        }

        node.append("circle")
            .attr("fill",
                (d) => {
                    switch (d.type) {
                        case "player-rm":
                            return "#FFFFFF";
                        case "player-bcn":
                            return "#C9002E";
                        case "referee":
                            return "#000000";
                        default:
                            return custom_colors(d.community)
                    }
                })
            .attr("r", 
                (d) => {
                    if (d.count === undefined) {
                        return 8;
                    }
                    else {
                        return ((((d.count - min_count) / (max_count - min_count))) * 20) + 5;
                    }
            })
            .style("stroke", 
                (d) => {                    
                    if (d.type == 'account') {
                        return custom_colors(d.community);
                    } else {
                        return '#918F00';
                    }
            })
            .style("stroke-width", 
                (d) => {
                    if (d.type == 'account') {
                        return '1px';
                    } else {
                        return '1.1px';
                    }
            })            
            .append("svg:title") //Title to player nodes when mouse hovering
            .text((d) => { return d.id + ((d.type == "account") ? "" : ", " + String(d.count) + " mentions"); });   

        //node.select("circle").forEach(collide(0.5));

        force.on("tick", function() {
            link.attr("x1", (d) => { return d.source.x; })
                    .attr("y1", (d) => { return d.source.y; })
                    .attr("x2", (d) => { return d.target.x; })
                    .attr("y2", (d) => { return d.target.y; });

            node.attr("transform", (d) => { return "translate(" + d.x + "," + d.y + ")"; });           
        });

/*        function collide(alpha) {
            var quadtree = d3.geom.quadtree(node);
            return function(d) {
                var r = d.radius + maxRadius + padding,
                        nx1 = d.x - r,
                        nx2 = d.x + r,
                        ny1 = d.y - r,
                        ny2 = d.y + r;
                quadtree.visit(function(quad, x1, y1, x2, y2) {
                    if (quad.point && (quad.point !== d)) {
                        var x = d.x - quad.point.x,
                                y = d.y - quad.point.y,
                                l = Math.sqrt(x * x + y * y),
                                r = d.radius + quad.point.radius + padding;
                        if (l < r) {
                            l = (l - r) / l * alpha;
                            d.x -= x *= l;
                            d.y -= y *= l;
                            quad.point.x += x;
                            quad.point.y += y;
                        }
                    }
                    return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
                });
            };
        }*/

    });
}());
