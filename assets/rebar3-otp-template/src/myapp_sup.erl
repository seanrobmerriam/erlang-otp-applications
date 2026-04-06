-module(myapp_sup).
-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    Worker = #{
        id => myapp_worker,
        start => {myapp_worker, start_link, []},
        restart => permanent,
        shutdown => 5000,
        type => worker,
        modules => [myapp_worker]
    },
    {ok, {{one_for_one, 10, 10}, [Worker]}}.
