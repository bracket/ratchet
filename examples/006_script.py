from ratchet.script import *

def main():
    import aifc

    # script = Script([
    #     'everything',
    #     -200,
    #     'in its right place',

    #     Voice('Kate', 'weasels'),
    #     -200,
    #     'in there right place'
    # ])

    # script = Script([
    #     'i have a boyfriend',
    #     'his name is oh-ryon',
    #     'he jumps in my laundry hamper',
    #     'and sleeps on my clean',
    #     Delay(-300), 'black',
    #     Delay(-300), 'slacks',
    # ])  

    script = Script([
        Marker('hello'),
        Voice('Daniel', 'hello'),
        Delay(-150),

        Marker('lets'),
        'lets do some euclid',
    ])  


    pcm, markers = script.render()

    with aifc.open('test.caff', 'wb') as out:
        out.setframerate(22050)
        out.setnchannels(1)
        out.setsampwidth(2)

        out.writeframes(pcm.tobytes())

    print(markers)


if __name__ == '__main__':
    main()
