
    // initialize global variables.
    var edges;
    var nodes;
    var network; 
    var container;
    var options, data;

    
    // This method is responsible for drawing the graph, returns the drawn network
    function drawGraph() {
        var container = document.getElementById('mynetwork');
        
        

        // parsing and collecting nodes and edges from the python
        nodes = new vis.DataSet([{"font": {"color": "white"}, "id": "00:10:7b:35:f5:b5", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_IPPhone_V1.png", "label": "00:10:7b:35:f5:b5", "shape": "image", "size": 20, "text": "00:10:7b:35:f5:b5"}, {"font": {"color": "white"}, "id": "00:10:7b:35:f5:c6", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Modem_V1.png", "label": "00:10:7b:35:f5:c6", "shape": "image", "size": 20, "text": "00:10:7b:35:f5:c6"}, {"font": {"color": "white"}, "id": "00:10:7b:35:f5:d7", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Modem_V1.png", "label": "00:10:7b:35:f5:d7", "shape": "image", "size": 20, "text": "00:10:7b:35:f5:d7"}, {"font": {"color": "white"}, "id": "00:10:7b:12:34:56", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Switch_V1.png", "label": "00:10:7b:12:34:56", "shape": "image", "size": 20, "text": "00:10:7b:12:34:56"}, {"font": {"color": "white"}, "id": "00:10:7b:78:91:23", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Switch_V1.png", "label": "00:10:7b:78:91:23", "shape": "image", "size": 20, "text": "00:10:7b:78:91:23"}, {"font": {"color": "white"}, "id": "00:10:7b:45:67:89", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Switch_V1.png", "label": "00:10:7b:45:67:89", "shape": "image", "size": 20, "text": "00:10:7b:45:67:89"}, {"font": {"color": "white"}, "id": "00:10:7b:24:68:13", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Switch_V1.png", "label": "00:10:7b:24:68:13", "shape": "image", "size": 20, "text": "00:10:7b:24:68:13"}, {"font": {"color": "white"}, "id": "94-ff-3c-1d-c9-05", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_FireWall_V1.png", "label": "94-ff-3c-1d-c9-05", "shape": "image", "size": 20, "text": "94-ff-3c-1d-c9-05"}, {"font": {"color": "white"}, "id": "fc:15:b4-1e-1d-77", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Servers_V1.png", "label": "fc:15:b4-1e-1d-77", "shape": "image", "size": 20, "text": "fc:15:b4-1e-1d-77"}, {"font": {"color": "white"}, "id": "F4-8E-38-EC-D7-10", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Laptop_V1.png", "label": "F4-8E-38-EC-D7-10", "shape": "image", "size": 20, "text": "F4-8E-38-EC-D7-10"}, {"font": {"color": "white"}, "id": "F4-8E-38-EC-E8-10", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Laptop_V1.png", "label": "F4-8E-38-EC-E8-10", "shape": "image", "size": 20, "text": "F4-8E-38-EC-E8-10"}, {"font": {"color": "white"}, "id": "F4-8E-38-EC-F9-10", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Laptop_V1.png", "label": "F4-8E-38-EC-F9-10", "shape": "image", "size": 20, "text": "F4-8E-38-EC-F9-10"}, {"font": {"color": "white"}, "id": "6C-E5-C9-98-76-54", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Desktop_V1.png", "label": "6C-E5-C9-98-76-54", "shape": "image", "size": 20, "text": "6C-E5-C9-98-76-54"}, {"font": {"color": "white"}, "id": "6C-E5-C9-78-90-23", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Desktop_V1.png", "label": "6C-E5-C9-78-90-23", "shape": "image", "size": 20, "text": "6C-E5-C9-78-90-23"}, {"font": {"color": "white"}, "id": "00-80-f0-a6-e4-99", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_IPPhone_V1.png", "label": "00-80-f0-a6-e4-99", "shape": "image", "size": 20, "text": "00-80-f0-a6-e4-99"}, {"font": {"color": "white"}, "id": "00-00-aa-37-32-36", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Printer_V1.png", "label": "00-00-aa-37-32-36", "shape": "image", "size": 20, "text": "00-00-aa-37-32-36"}, {"font": {"color": "white"}, "id": "6C-E5-C9-12-34-56", "image": "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Desktop_V1.png", "label": "6C-E5-C9-12-34-56", "shape": "image", "size": 20, "text": "6C-E5-C9-12-34-56"}]);
        edges = new vis.DataSet([{"color": "lightblue", "from": "00:10:7b:35:f5:b5", "to": "00:10:7b:35:f5:c6", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:35:f5:b5", "to": "00:10:7b:35:f5:d7", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:35:f5:c6", "to": "00:10:7b:12:34:56", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:35:f5:c6", "to": "00:10:7b:78:91:23", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:35:f5:d7", "to": "00:10:7b:45:67:89", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:35:f5:d7", "to": "00:10:7b:24:68:13", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:12:34:56", "to": "94-ff-3c-1d-c9-05", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:12:34:56", "to": "fc:15:b4-1e-1d-77", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:78:91:23", "to": "F4-8E-38-EC-D7-10", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:78:91:23", "to": "F4-8E-38-EC-E8-10", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:45:67:89", "to": "F4-8E-38-EC-F9-10", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:45:67:89", "to": "6C-E5-C9-98-76-54", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:24:68:13", "to": "6C-E5-C9-78-90-23", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:24:68:13", "to": "00-80-f0-a6-e4-99", "weight": 4}, {"color": "lightblue", "from": "00:10:7b:24:68:13", "to": "00-00-aa-37-32-36", "weight": 4}, {"color": "lightblue", "from": "00-80-f0-a6-e4-99", "to": "6C-E5-C9-12-34-56", "weight": 4}]);

        // adding nodes and edges to the graph
        data = {nodes: nodes, edges: edges};

        var options = {"configure": {"enabled": false, "filter": true}, "edges": {"color": {"inherit": true}, "smooth": {"enabled": false, "type": "continuous"}}, "interaction": {"hover": true, "dragNodes": true, "hideEdgesOnDrag": false, "hideNodesOnDrag": false, "navigationButtons": true}, "physics": {"enabled": true, "stabilization": {"enabled": true, "fit": true, "iterations": 1000, "onlyDynamicEdges": false, "updateInterval": 50}}};
        
        

        

        network = new vis.Network(container, data, options);
	 
        


        

        return network;

    }

    drawGraph();