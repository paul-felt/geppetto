
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

    <!-- Episode switch -->
    <h3>Episode Recording</h3>
    <!-- widget/styling from https://proto.io/freebies/onoff/ -->
    <div class="onoffswitch">
        <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="episode-recorder">
        <label class="onoffswitch-label" for="episode-recorder">
            <span class="onoffswitch-inner"></span>
            <span class="onoffswitch-switch"></span>
        </label>
    </div>

    <!-- Controls -->
    <h3>Controls</h3>
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
                   document.location.hostname + ":5555" + "/ws";
    }
    // the WAMP connection to the Router
    //
    var connection = new autobahn.Connection({
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

    function buildEpisodeToggle(session){
      $('#episode-recorder').change(function(){
        checked = $('#episode-recorder').is(':checked');
        // publish this control change back to whoever is listening (robot)
        var message = {
          value : checked ? 'begin' : 'end',
          robot_name : self.robot_name,
          name : 'episode',
          type : 'episode',
          source : 'web',
          ts : new Date().getTime(),
        }
        session.publish(`gp.robots.${self.robot_name}.episodes`, null, message);
      });
    };

    function buildControlSliders(session){
      for (control_idx in self.controls){
        var control = self.controls[control_idx]
        var control_name = control['control_name'];
        var channel_name = control['channel_name'];
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

        // we need to create a closure to keep the right channel_name in scope for our callback
        (function(channel_name, control_name){
          // slider activate: start a timer going until we release this slider
          slider.noUiSlider.on('start',function(values, handle, unencoded, tap, positions ){		
          currSlider = this;
          timer=setInterval(function(){
                // publish this control change back to whoever is listening (robot)
                var message = {
                  value : currSlider.get(),
                  robot_name : self.robot_name,
                  name : control_name,
                  type : 'control',
                  source : 'web',
                  ts : new Date().getTime(),
                }
                session.publish(channel_name, null, message);
              }, 20); // the above code is executed every 20 ms
          })

          // slider release: cancel the timer
          slider.noUiSlider.on('end',function(values, handle, unencoded, tap, positions ){		
            if (timer) clearInterval(timer)
          })
          // single slider set. one and done
          slider.noUiSlider.on('set',function(values, handle, unencoded, tap, positions ){		
            // publish this control change back to whoever is listening (robot)
            var message = {
              value : values[0],
              robot_name : self.robot_name,
              name : control_name,
              type : 'control',
              source : 'web',
              ts : new Date().getTime(),
            }
            session.publish(channel_name, null, message);
          })
          //slider.noUiSlider.destroy()
        })(channel_name, control_name);
      } // end for controls

    } // end build sliders

    // utility function to interpret base64-encoded binary sensor data
    // (see https://stackoverflow.com/questions/16245767/creating-a-blob-from-a-base64-string-in-javascript)
    function base64toBlob(base64Data, contentType) {
      contentType = contentType || '';
      var sliceSize = 1024;
      var byteCharacters = atob(base64Data);
      var bytesLength = byteCharacters.length;
      var slicesCount = Math.ceil(bytesLength / sliceSize);
      var byteArrays = new Array(slicesCount);

      for (var sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
          var begin = sliceIndex * sliceSize;
          var end = Math.min(begin + sliceSize, bytesLength);

          var bytes = new Array(end - begin);
          for (var offset = begin, i = 0; offset < end; ++i, ++offset) {
              bytes[i] = byteCharacters[offset].charCodeAt(0);
          }
          byteArrays[sliceIndex] = new Uint8Array(bytes);
      }
      return new Blob(byteArrays, { type: contentType });
    }

    function buildSensorDisplays(session){
      for (sensor_idx in self.sensors){
        var sensor = self.sensors[sensor_idx]
        var channel_name = sensor['channel_name'];
        var sensor_name = sensor['sensor_name'];

        // closure to keep sensor name in scope
        (function(sensor_name,channel_name){
          // now we're going to subscribe to this sensor's messages
          session.subscribe(channel_name, function(args, kwargs, details){
            try{ // autobahn swallows errors, so catch them ourselves
              // we got a sensor message
              //console.log(`got video for ${sensor_name}: ${data}`);
              data = kwargs.value 
              // WAMP protocol specifies that if the first bytes is \0
              // then the payload should be interpreted as base64. In the 
              // future autobahn should do this for us, but not yet:
              // see: https://github.com/crossbario/autobahn-js/issues/189
              if (data[0] === '\0'){
                data = data.substring(1);
              }
              blob = base64toBlob(data, 'image/jpeg');
              var objectUrl = URL.createObjectURL(blob);
              $(`#sensor_${sensor_name}`).attr("src",objectUrl);
            }
            catch(err){
              console.error('failed to parse sensor data: ',err);
            }
          }).then(
            function (sub){
              console.log('we successfully subscribed to sensor stream', sub);
            },
            function (err){
              console.log('we failed to subscribe to sensor stream', err);
            }
          );
        // end closure
        })(sensor_name,channel_name);

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
        robot_name: robot_name,
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
          buildEpisodeToggle(session);
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

    #slider{
      /*height:500px;*/
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

    img {
      height: 300px;
    }

    /* Toggle slider styling */
    .onoffswitch {
        display: inline-block; 
        position: relative; width: 200px;
        -webkit-user-select:none; -moz-user-select:none; -ms-user-select: none;
    }
    .onoffswitch-checkbox {
        display: none;
    }
    .onoffswitch-label {
        display: block; overflow: hidden; cursor: pointer;
        border: 2px solid #999999; border-radius: 20px;
    }
    .onoffswitch-inner {
        display: block; width: 200%; margin-left: -100%;
        transition: margin 0.3s ease-in 0s;
    }
    .onoffswitch-inner:before, .onoffswitch-inner:after {
        display: block; float: left; width: 50%; height: 30px; padding: 0; line-height: 30px;
        font-size: 14px; color: white; font-family: Trebuchet, Arial, sans-serif; font-weight: bold;
        box-sizing: border-box;
    }
    .onoffswitch-inner:before {
        content: "Recording";
        padding-left: 10px;
        background-color: #71D13D; color: #FFFFFF;
    }
    .onoffswitch-inner:after {
        content: "Off";
        padding-right: 10px;
        background-color: #EEEEEE; color: #999999;
        text-align: right;
    }
    .onoffswitch-switch {
        display: block; width: 22px; margin: 4px;
        background: #FFFFFF;
        position: absolute; top: 0; bottom: 0;
        right: 166px;
        border: 2px solid #999999; border-radius: 20px;
        transition: all 0.3s ease-in 0s; 
    }
    .onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-inner {
        margin-left: 0;
    }
    .onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-switch {
        right: 0px; 
    }

  </style>

</app-main>

