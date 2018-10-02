<app-main>

  <article>
    <h1>{ title }</h1>
    <p>{ description }</p>
    <robot-detail>
  </article>

  <robot-detail>
    <!-- Sensors -->
    <h3>Sensors</h3>
    <ul>
      <li each={ sensors }><image id="sensor_{sensor_name}"></image></li>
    </ul>
    <!-- Controls -->
    <h3>Controls</h3>
    <div each={ controls }>
      <p> { control_name } </p>
      <div id="slider_{control_name}"></div>
    </div>
  </robot-detail>


  <script>
    var socket = io();

    var self = this
    self.title = 'Loading...'
    self.description = ''

    var r = route.create()
    r('',        home       )
    r('*',   robot_page      )
    r(           home       ) // `notfound` would be nicer!

    function buildSliders(){
      for (control_idx in self.controls){
        var control = self.controls[control_idx]
        var control_name = control['control_name'];
        var control_limits = control['limits'];
        // SLIDER
        var slider=document.getElementById(`slider_${control_name}`);
        noUiSlider.create(slider, {
          start: 20, //num, [num], [num,num]
          range: {
            'min': control_limits[0],
            'max': control_limits[1]
          },
          behaviour: 'drag-tap',
          connect: true,
          //margin: 30,
          //limit: 40,
          //step: 1,
          orientation: 'horizontal',
          animate: true,
        	animationDuration: 300,
          tooltips:true //[true,true]
        });

        var timer;

        // we need to create a closure to keep the right control_name in scope for our callback
        (function(control_name){
          // slider activate: start a timer going until we release this slider
          slider.noUiSlider.on('start',function(values, handle, unencoded, tap, positions ){		
          currSlider = this;
          timer=setInterval(function(){
                $.post(`/robots/${self.robot_name}/controls/${control_name}`, currSlider.get());
              }, 20); // the above code is executed every 100 ms
          })

          // slider release: cancel the timer
          slider.noUiSlider.on('end',function(values, handle, unencoded, tap, positions ){		
            if (timer) clearInterval(timer)
          })
          // single slider set. one and done
          slider.noUiSlider.on('set',function(values, handle, unencoded, tap, positions ){		
            $.post(`/robots/${self.robot_name}/controls/${control_name}`, values[0]);
          })
          //slider.noUiSlider.destroy()
        })(control_name);
      } // end for controls

    } // end build sliders

    function openSockets(){
      for (sensor_idx in self.sensors){
        var sensor = self.sensors[sensor_idx]
        var sensor_socketio = sensor['socketio'];
        var sensor_name = sensor['sensor_name'];
        // closure to keep sensor name in scope
        (function(sensor_name){
          socket.on(sensor_socketio, function(data){
            console.log(`got video for ${sensor_name}: ${data}`);
            var blob = new Blob([data], { type: 'image/jpeg' });
            var objectUrl = URL.createObjectURL(blob);
            $(`#sensor_${sensor_name}`).attr("src",objectUrl);
          });
        })(sensor_name);
      }
    }

    function home() {
      self.update({
        title:  "Welcome to Geppetto",
        description:  "Your robots are listed in tabs"
      })
    }

    function robot_page(robot_name) {
      self.update({
        title:  robot_name,
        description:  "Loading...",
        controls: [],
        sensors: [],
      });
      $.get(`/robots/${robot_name}`, function(robot_info){
        robot_info['description'] = ''; 
        self.update(robot_info)
        buildSliders();
        openSockets();
      });
    }

  </script>

  <style>
    :scope {
      display: block;
      font-family: sans-serif;
      margin-right: 0;
      margin-bottom: 130px;
      margin-left: 50px;
      padding: 1em;
      text-align: center;
      color: #666;
    }
    ul {
      padding: 10px;
      list-style: none;
    }
    li {
      display: inline-block;
      margin: 5px;
    }
    a {
      display: block;
      background: #f7f7f7;
      text-decoration: none;
      width: 150px;
      height: 150px;
      line-height: 150px;
      color: inherit;
    }
    a:hover {
      background: #eee;
      color: #000;
    }
    @media (min-width: 480px) {
      :scope {
        margin-right: 200px;
        margin-bottom: 0;
      }
    }

    #slider{
      //height:500px;
    }
    #slider > .noUi-base {
      background: #c0392b;  
    }
    #slider  {
      background: #50ab2b;  
    }
    #slider  {
      background: #80392d;  
    }
    .noUi-tooltip {
        display: none;
    }
    .noUi-active .noUi-tooltip {
        display: block;
    }

  </style>

</app-main>

