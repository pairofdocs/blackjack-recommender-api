"""API
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from importer.StrategyImporter import StrategyImporter
importer = StrategyImporter("./strategy/BasicStrategy.csv")

HARD_STRATEGY, SOFT_STRATEGY, PAIR_STRATEGY = importer.import_player_strategy()
SOFT_STRATEGY[22] = {'Player': 'AA','Two': 'P','Three': 'P','Four': 'P','Five': 'P','Six': 'P','Seven': 'P','Eight': 'P','Nine': 'P','Ten': 'P','Jack': 'P','Queen': 'P','King': 'P','Ace': 'P'}

class Item(BaseModel):
    playercard1: str
    playercard2: str
    dealer: str

app = FastAPI()
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://0.0.0.0",
    "https://blackjack-trainer.net"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/strat")
async def recommendation(item: Item):
    recommendation, table = strategy(item.playercard1, item.playercard2, item.dealer)
    return {'recommend': recommendation, 'table_used': table}


def card_str_to_int(card_str):
    card_value = 0
    if card_str.lower() in ['j', 'q', 'k']:
        card_value = 10
    elif card_str.lower() == 'a':
        card_value = 11
    else:
        card_value = int(card_str)
    return card_value


def strategy(playercard1, playercard2, dealer):
    """
    playercard1,2 value     e.g. 4,4
    """
    playercard1, playercard2 = card_str_to_int(playercard1), card_str_to_int(playercard2)

    # dealer
    char_to_str = {'2':'Two', '3':'Three', '4':'Four', '5':'Five', '6':'Six', '7':'Seven', '8':'Eight', '9':'Nine', 't':'Ten', 'j':'Jack', 'q':'Queen', 'k':'King', 'a':'Ace'}
    dealer = char_to_str[dealer.lower()]
    print(playercard1, playercard2, 'vs', dealer)

    value = playercard1 + playercard2
    table_used = 'hard_strat'
    if playercard1 == 11 or playercard2 == 11:  # NOTE: ace ace is split. in soft strat
        recommendation = SOFT_STRATEGY[value][dealer]
        table_used = 'soft_strat'
    elif playercard1 == playercard2:
        recommendation = PAIR_STRATEGY[value][dealer]
        table_used = 'pair_strat'
    else:
        recommendation = HARD_STRATEGY[value][dealer]

    return recommendation, table_used


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

#  curl -X POST 127.0.0.1:8000/strat -H "Content-Type: application/json" -d '{"playercard1":"4", "playercard2":"4", "dealer":"3"}'


# p1 = document.getElementById("player1").children[0].attributes[0].value[0];
# p2 = document.getElementById("player1").children[1].attributes[0].value[0];
# dl = document.getElementById("dealer").children[1].attributes[0].value[0];
# payload = {
#     playercard1: p1,
#     playercard2: p2,
#     dealer: dl
# };
# fetch('http://127.0.0.1:8000/strat', {
#   method: 'POST',
#   headers: {
#     'Accept': 'application/json, text/plain, */*',
#     'Content-Type': 'application/json'
#   },
#   body: JSON.stringify(payload)
# }).then(res => res.json()).then(json => console.log(json))
