<app-navi>

  <a each={ opts.robots } href="#{ robot_name }" class={ selected: parent.selectedId === robot_name }>
    { robot_short_name }
  </a>

  <script>
    var self = this

    var r = route.create()
    r(highlightCurrent)

    // What do we call robots in the sidebar? 
    // For now just a number
    function computeShortName(robot_name, idx){
      return idx;
    }

    var i;
    for (i = 0; i<self.opts.robots.length; i++){
      self.opts.robots[i]['robot_short_name'] = computeShortName(self.opts.robots[i], i+1);
    }

    function highlightCurrent(id) {
      self.selectedId = id
      self.update()
    }
  </script>

  <style>
    :scope {
      position: fixed;
      top: 0;
      left: 0;
      height: 100%;
      box-sizing: border-box;
      font-family: sans-serif;
      text-align: center;
      color: #666;
      background: #333;
      width: 50px;
      transition: width .2s;
    }
    :scope:hover {
      width: 60px;
    }
    a {
      display: block;
      box-sizing: border-box;
      width: 100%;
      height: 50px;
      line-height: 50px;
      padding: 0 .8em;
      color: white;
      text-decoration: none;
      background: #444;
    }
    a:hover {
      background: #666;
    }
    a.selected {
      background: teal;
    }
  </style>

</app-navi>

