<style>
div.app {
  margin: 0 10px 0 10px;
}

div.poem {
  margin: 0 0 5px 0;
  padding: 5px 5px 0 5px;
}

p.focused {
  color: orange;
}

span.title {
  font-size: 150%;
}

span.author {
  font-size: 90%;
}

</style>

<div class="app">
  <h1>唐诗搜索</h1>

  <div class="input">
    <form action="">
      关键词: <input type="text" name="keyword" value="{{keyword}}">
      <input type="submit">
    </form>
  </div>

  <div class="results">
  % for item in results:
      <div class="poem" style="border-style:solid;border-width:2px;border-radius:5px;">
      <div class="header">
        <span class="title"> {{item["content"]["title"]}} </span>
        <span class="author">( {{item["content"]["author"]}} )</span>
      </div>
      % for idx, p in enumerate(item["content"]["paragraphs"]):
	% if idx == item["paragraph"]:
        <p class="paragraph focused">{{p}}</p>
        % else:
        <p class="paragraph">{{p}}</p>
        % end
      % end
      </div>
  % end
  </div>

</div>
