(function(){
    Math.seedrandom('5'); 

    var width = 1920,
            height = 1080

    var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height)
            .call(d3.behavior.zoom().on("zoom", function () {
                svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
                }))
            .append("g");

    var pattern_def = svg.append("defs");

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
            .attr("r", 
                (d) => {
                    if (d.count === undefined) {
                        return 8;
                    }
                    else {
                        return ((((d.count - min_count) / (max_count - min_count))) * 20) + 5;
                    }
            })
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
            .style("stroke", 
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
            .style("stroke-width", 
                (d) => {
                    if (d.type == 'account') {
                        return '1px';
                    } else {
                        return '2.5px';
                    }
            })
            .each(function(d,i) {
                if ('img' in d) {
                    // append image pattern for each node
                    switch(d.id) {
                        case 'zidane':
                            d.img = 'http://theworldgame.sbs.com.au/sites/sbs.com.au.theworldgame/files/styles/full/public/20160529001260266484-original.jpg';
                            break;
                        case 'messi':
                            d.img = 'http://static.goal.com/4321800/4321812_news.jpg';
                            break;
                        case 'busquets':
                            d.img = 'https://clickon-media-soccer.s3.amazonaws.com/2016/02/diver.jpg';
                            break;
                    }
                    

                    pattern_def.append("pattern")
                            .attr("id", "node-img" + i)
                            .attr("patternUnits", "objectBoundingBox")
                            .attr({
                                "width": "100%",
                                "height": "100%"
                            })
                            .attr({
                                "viewBox": "0 0 1 1"
                            })
                            .append("image")
                            .attr("xlink:href", d.img)
                            .attr({
                                "x": 0,
                                "y": 0,
                                "width": "1",
                                "height": "1",
                                "preserveAspectRatio": "none"
                            });

                    d3.select(this).attr("fill", "url(#node-img" + i + ")");
                }
            })            
            .append("svg:title") //Title to player nodes when mouse hovering
            .text((d) => { return d.id + ((d.type == "account") ? "" : ", " + String(d.count) + " mentions"); });   

        node.on('dblclick', function (d) {
            if (d.id != 'messi' && d.id != 'busquets' && d.id != 'zidane') {
                window.open('https://twitter.com/' + d.id, '_blank');
            } else {
                window.open('https://www.google.es/search?q=' + d.id, '_blank');
            }            
        })

        force.on("tick", function() {
            link.attr("x1", (d) => { return d.source.x; })
                    .attr("y1", (d) => { return d.source.y; })
                    .attr("x2", (d) => { return d.target.x; })
                    .attr("y2", (d) => { return d.target.y; });

            node.attr("transform", (d) => { return "translate(" + d.x + "," + d.y + ")"; });           
        });
    });
}());
