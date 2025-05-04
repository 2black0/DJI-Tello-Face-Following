import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.set_facecolor((0,0,0))

def animate(i):
	ax.clear()
	xs = []
	ys = []
	graph_data = open('file.csv','r').read()
	lines = graph_data.split('\n')
	for line in lines[1:]:
		if len(line) > 1:
			x, y = line.split(',')
			xs.append(float(x))
			ys.append(float(y))
			print(xs,ys)
	
	ax.clear()
	ax.plot(xs, ys,'-o', color = (0,1,0.25))
	ax.set_xlabel("Error")
	ax.set_ylabel("Time")
	ax.set_title("Error of X Axis")
	fig.tight_layout()
	ax.yaxis.grid(True)

ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()