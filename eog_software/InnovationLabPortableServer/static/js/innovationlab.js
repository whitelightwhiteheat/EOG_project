
app = angular.module('app', []);

app.controller('AppCtrl', function($scope, $http) {
});


app.controller('DashboardCtrl', function($scope, $http) {

  $scope.games = [];

  var getData = function() {
    $http.get('/innovationlab/games/status')
     .then(function(response) {
       var data = response.data;
       $scope.games = [];
       for (var gamename in data) {
         var players = [];
         for (var username in data[gamename]) {
  	 if (username[0] != "_") {
             players.push({
               name : username,
               x        : data[gamename][username][0],
               y        : data[gamename][username][1],
               type     : data[gamename][username][2],
               noidea   : data[gamename][username][3],
               points   : data[gamename][username][4],
               haspwd   : data[gamename][username][5],
               password : data[gamename][username][6]
  	   });
  	 }
         }
         $scope.games.push({
           name: gamename,
   	 i:parseFloat(gamename.replace("spel","")),
           defenders : data[gamename]._defenders,
           attackers : data[gamename]._attackers,
  	 players : players
         });
       }
     });
  };

  $scope.resetGame = function(game) {
    $http.get('/innovationlab/'+game.name+'/reset')
      .then(function() {
        $scope.update();
      });
  };

  $scope.update = function() {
    getData();
  };

  $scope.update();

});


app.controller('LogCtrl', function($scope, $http, $interval) {

  $scope.reverse = true;
  $scope.logs = [];
  $scope.readloglines = 1000;

  var getData = function() {
    $http.get('/innovationlab/log/'+$scope.readloglines)
     .then(function(response) {
       var data = response.data;
       $scope.logs = data;
     });
  };

  $scope.update = function() {
    getData();
  };

  getData();
  $interval(function() {
    getData();
  }, 10000); 

});
