-module(myapp_worker).
-behaviour(gen_server).

-export([start_link/0, get_state/0]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-record(state, {
    started_at
}).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

get_state() ->
    gen_server:call(?MODULE, get_state).

init([]) ->
    {ok, #state{started_at = erlang:system_time(millisecond)}}.

handle_call(get_state, _From, State) ->
    {reply, State, State};
handle_call(Request, _From, State) ->
    {stop, {unexpected_call, Request}, State}.

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
