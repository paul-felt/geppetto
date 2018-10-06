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
      <li each={ sensors }>
        <image if={mediatype==="video"} id="sensor_{sensor_name}"></image>
        <!-- TODO: support other mediatypes -->
        <audio if={mediatype==="mp3"} id="sensor_{sensor_name}"></audio>
      </li>
    </ul>
    <!-- Controls -->
    <h3>Controls</h3>
    <ul>
    <div each={ controls }>
      <p> { control_name } </p>
      <div id="slider_{control_name}"></div>
    </div>
  </robot-detail>


  <script>
    // the URL of the WAMP Router (Crossbar.io)
    //
    var wsuri;
    if (document.location.origin == "file://") {
       wsuri = "ws://127.0.0.1:5555/ws";
    } else {
       wsuri = (document.location.protocol === "http:" ? "ws:" : "wss:") + "//" +
                   document.location.host + "/ws";
    }
    // the WAMP connection to the Router
    //
    var socket = new autobahn.Connection({
       url: wsuri,
       realm: "realm1"
    });

    var self = this
    self.title = 'Loading...'
    self.description = ''

    var r = route.create()
    r('',        home       )
    r('*',   robot_page      )
    r(           home       ) // `notfound` would be nicer!

    function buildControlSliders(session){
      for (control_idx in self.controls){
        var control = self.controls[control_idx]
        var control_name = control['control_name'];
        var control_socketio = control['control_socketio'];
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

        // we need to create a closure to keep the right control_socketio in scope for our callback
        (function(control_socketio){
          // slider activate: start a timer going until we release this slider
          slider.noUiSlider.on('start',function(values, handle, unencoded, tap, positions ){		
          currSlider = this;
          timer=setInterval(function(){
                // publish this control change back to whoever is listening (robot)
                session.publish(control_socketio, currSlider.get());
              }, 20); // the above code is executed every 20 ms
          })

          // slider release: cancel the timer
          slider.noUiSlider.on('end',function(values, handle, unencoded, tap, positions ){		
            if (timer) clearInterval(timer)
          })
          // single slider set. one and done
          slider.noUiSlider.on('set',function(values, handle, unencoded, tap, positions ){		
            // publish this control change back to whoever is listening (robot)
            session.publish(control_socketio, values[0]);
          })
          //slider.noUiSlider.destroy()
        })(control_socketio);
      } // end for controls

    } // end build sliders

    function buildSensorDisplays(session){
      for (sensor_idx in self.sensors){
        var sensor = self.sensors[sensor_idx]
        var sensor_socketio = sensor['socketio'];
        var sensor_name = sensor['sensor_name'];

        // closure to keep sensor name in scope
        (function(sensor_name){
          // now we're going to subscribe to this sensor's messages
          session.subscribe(sensor_socketio, function(data){
            // we got a sensor message
            console.log(`got video for ${sensor_name}: ${data}`);
            var blob = new Blob([data], { type: 'image/jpeg' });
            var objectUrl = URL.createObjectURL(blob);
            $(`#sensor_${sensor_name}`).attr("src",objectUrl);
          }).then(
            function (sub){
              console.log('we successfully subscribed to sensor stream', sub);
            },
            function (err){
              console.log('we failed to subscribe to sensor stream', err);
            }
          );
        // end closure
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
        // open a connection with the WAMP server before building our components
        connection.onopen = function(session, details){
          console.log('connection to WAMP server opened');
          buildControlSliders(session);
          buildSensorDisplays(session);
        };
        // connection failed/closed
        connection.onclose = function(reason, details){
          console.log('connection to WAMP server closed:' + reason);
        };
        connection.open();
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

