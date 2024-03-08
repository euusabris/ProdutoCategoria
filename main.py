import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, relationship, Session
from sqlalchemy import (Column, Uuid, String, DateTime, func, DECIMAL, Integer, Boolean, ForeignKey)

motor = create_engine("sqlite+pysqlite:///banco_de_dados.sqlite", echo=True)



class Base(DeclarativeBase):
    pass

class DatasMixin:
    dta_cadastro = Column(DateTime, server_default=func.now(), nullable=False)
    dta_atualizada = Column(DateTime, onupdate=func.now(), default=func.now(), nullable=False)
class Categoria(Base, DatasMixin):

    __tablename__ = "tbl_categorias"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(256), nullable=False)

    lista_de_produtos = relationship("Produto", back_populates="categoria", cascade="all, delete-orphan", lazy="selectin")
class Produto(Base, DatasMixin):
    __tablename__ = "tbl_produtos"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(256), nullable=False)
    preco = Column(DECIMAL(10, 2), default=0.00)
    estoque = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    categoria_id = Column(Uuid(as_uuid=True), ForeignKey("tbl_categorias.id"))

    categoria = relationship("Categoria", back_populates="lista_de_produtos")


# cat = Categoria()
# cat.nome = "Bebidas"
#
# prod = Produto()
# prod.nome = "Coca cola zero, 2L"
# prod.ativo = True
# prod.preco = 9.50
# prod.estoque = 100
# prod.categoria = cat
#
#
#
# with Session(motor) as sessao:
#     sessao.add(prod)
#     sessao.commit()

# with Session(motor) as sessao:
#     lista_de_categorias = sessao.execute(select(Categoria)).scalars()
#     for categoria in lista_de_categorias:
#         print(f"A categoria {categoria.nome} tem {len(categoria.lista_de_produtos)} produtos")
#         for produto in categoria.lista_de_produtos:
#             print(f" Produto {produto.nome} que tem {produto.estoque} unidades no estoque")

def seed_database():
    # iterar sobre as categorias e adicionar os produtos

    with Session(motor) as sessao:

        if sessao.execute(select(Categoria).limit(1)).scalar_one_or_none():
            return
        from seed import seed_data
        for categoria in seed_data:
            cat = Categoria()
            print(f"Semeando a categoria {categoria['categoria']}...")
            cat.nome = categoria["categoria"]
            for produto in categoria['produtos']:
                p = Produto()
                p.nome = produto["nome"]
                p.preco = produto["preco"]
                p.estoque = 0
                p.ativo = True
                p.categoria = cat
                sessao.add(p)
            sessao.commit()
def incluir_categoria():
    print("Incluindo categoria")
    nome = input("Qual o nome da categoria que você quer adicionar? ")
    with Session(motor) as sessao:
        categoria = Categoria()
        categoria.nome = nome
        sessao.add(categoria)
        sessao.commit()
    print(f"Categoria {nome} adicionada.")


def listar_categorias():
    print("Categorias cadastradas")
    print(f"Nome                                      # Produtos")
    print(f"----------------------------------------- ----------")
    stmt = select(Categoria)
    stmt = stmt.order_by("nome")
    with Session(motor) as sessao:
        rset = sessao.execute(stmt).scalars()
        for categoria in rset:
            print(f"{categoria.nome:40s}  {len(categoria.lista_de_produtos):10d}")
            # for produto in categoria.lista_de_produtos:
            #     print(f"   {produto.nome}")
    print(f"----------------------------------------- ----------")

def seleciona_categoria():
    nome_parcial = input("Digite uma parte do nome da categoria desejada: ")
    # select * from categorias where categorias,.nome LIKE "%...%"
    stmt = select(Categoria).where(Categoria.nome.ilike(f"%{nome_parcial}%")).order_by("nome")
    with Session(motor) as sessao:
        rset = sessao.execute(stmt).scalars()
        contador = 1
        ids = list()
        for categoria in rset:
            print(f"{contador:3d} - {categoria.nome}")
            contador = contador + 1
            ids.append(categoria.id)
        cod = int(input("Digite o numero da categoria desejada: "))
        categoria = ids[cod - 1]
    return categoria

def alterar_categoria():
    id_categoria = seleciona_categoria()
    with Session(motor) as sessao:
        categoria = sessao.get(Categoria, id_categoria)
        print(f"Nome atual categoria: {categoria.nome}")
        novo_nome = input("Qual vai ser o novo nome: ")
        categoria.nome = novo_nome
        sessao.commit()
    return
def remover_categoria():
    id_categoria = seleciona_categoria()
    with Session(motor) as sessao:
        categoria = sessao.get(Categoria, id_categoria)
        print(f"ATENÇÃO! Ao removera categoria '{categoria.nome}' você vai "
              f"remover também, {len(categoria.lista_de_produtos)} produtos vinculados")
        for produto in categoria.lista_de_produtos:
            print(f"   - {produto.nome}")
        resposta = input("Remove mesmo assim (S/N)?")
        if resposta.upper() == "S":
            sessao.delete(categoria)
            sessao.commit()
        else:
            print("Mantendo a categoria no banco...")
    return

if __name__ == "__main__":
    seed_database()
    while True:
        print("Menu de opcoes")
        print("1. Incluir categoria")
        print("2. Listar categorias")
        print("3. Alterar categoria")
        print("4. Remover categoria")
        print("0. Sair")
        opcao = int(input("Qual opcao? "))
        if opcao == 1:
            incluir_categoria()
        elif opcao == 2:
            listar_categorias()
        elif opcao == 3:
            alterar_categoria()
        elif opcao == 4:
            remover_categoria()

        elif opcao == 0:
            exit(0)

        else:
            print("Opcao invalida...")


