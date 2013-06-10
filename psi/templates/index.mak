<html>
<head>
</head>
<body>
  <h1></h1>


  <h2>Profiles</h2>
  <ul>
    % for name in filenames:
      <li><a href="/view/${name}">${name}</a></li>
    % endfor
  </ul>

</body>
</html>
