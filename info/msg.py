class ExampleMessage():
	def __init__(my, str="Hello world!"):
		my.id = my.__class__.__name__
		my.str = str
	def __str__(my):
		return json.dumps(my.__dict__)
