<app-main>

  <article>
    <h1>{ title }</h1>
    <p>{ body }</p>
    <ul if={ isFirst }>
      <li each={ data }><a href="#first/{ id }">{ title }</a></li>
    </ul>
    <div id="slider"></div>
  </article>

  <script>
    var self = this
    self.title = 'Now loading...'
    self.body = ''
    self.data = [
      { id: 'apple', title: 'Apple', body: "The world biggest fruit company." },
      { id: 'orange', title: 'Orange', body: "I don't have the word for it..." }
    ]

    var r = route.create()
    r('',        home       )
    r('first',   first      )
    r('first/*', firstDetail)
    r('second',  second     )
    r(           home       ) // `notfound` would be nicer!

    function home() {
      self.update({
        title:  "Home of the great app",
        body:  "Timeline or dashboard as you like!",
        isFirst: false
      })
    }
    function first() {
      self.update({
        title: "First feature of your app",
        body: "It could be a list of something for example.",
        isFirst: true
      })
    }
    function firstDetail(id) {
      var selected = self.data.filter(function(d) { return d.id == id })[0] || {}
      self.update({
        title: selected.title,
        body: selected.body,
        isFirst: false
      })
    }
    function second() {
      self.update({
        title: "Second feature of your app",
        body: "It could be a config page for example.",
        isFirst: false
      })
    }

    // only instantiate the slider after the page/tag has mounted so we can find the 'slider' id in the doc
    this.on('mount', function(){
      // SLIDER
      var slider=document.getElementById('slider');
      noUiSlider.create(slider, {
        start: [20,40], //num, [num], [num,num]
        range: {
          'min': [0],
          'max': [100]
        },
        behaviour: 'drag-tap',
        connect: true,
        //margin: 30,
        //limit: 40,
        step: 10,
        orientation: 'horizontal',
        animate: true,
      	animationDuration: 300,
        tooltips:[true,true]
      });
      slider.noUiSlider.on('slide',function(values, handle, unencoded, tap, positions ){		
         var tempSlider=$(slider);
        tempSlider.find('.noUi-base').css('background','red');
        tempSlider.find('.noUi-base > .noUi-connect').css('background','green');
        tempSlider.find('.noUi-base .noUi-handle.noUi-handle-lower').css('background','green');
        tempSlider.find('.noUi-base .noUi-handle.noUi-handle-upper').css('background','pink');
        tempSlider.find('.noUi-base > .noUi-connect').css('background','green');
        tempSlider.find('.noUi-base > .noUi-background').css('background','blue');
      })
      //slider.noUiSlider.destroy()
    });
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

