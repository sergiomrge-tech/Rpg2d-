extends Node2D
## Entry scene: everything else is built in code by the Game autoload.


func _ready() -> void:
	Game.start(self)
