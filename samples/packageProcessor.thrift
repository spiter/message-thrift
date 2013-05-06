
namespace cpp package

struct PPHelloPackage
{
1: string word,
}

service ClientService {
    oneway void hello(1: PPHelloPackage helloPackage)
    oneway void friendBlinks(1: string friendName)
}

service ServerService {
    oneway void introduce(1: string clientName)
    oneway void blink()
}

