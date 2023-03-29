def fix_contig(contig, parsed_pdb):
  INF = float("inf")
  X = contig.split("/")
  for n,x in enumerate(X):
    if x[0].isalpha():
      C,x = x[0],x[1:]
      S,E = -INF,INF
      if x.startswith("-"):
        E = int(x[1:])
      elif x.endswith("-"):
        S = int(x[:-1])
      elif "-" in x:
        (S,E) = (int(y) for y in x.split("-"))
      elif x.isnumeric():
        S = E = int(x)
      new_x = ""
      c_,i_ = None,0
      for c, i in parsed_pdb["pdb_idx"]:
        if c == C and i >= S and i <= E:
          if c_ is None:
            new_x = f"{c}{i}"
          else:
            if c != c_ or i != i_+1:
              new_x += f"-{i_}/{c}{i}"
          c_,i_ = c,i
      X[n] = new_x + f"-{i_}"
    if x.isnumeric() and x != "0":
      X[n] = f"{x}-{x}"
  return "/".join(X)

def fix_pdb(pdb_str, contigs):
  def get_range(contig):
    L_init = 1
    R = []
    sub_contigs = [x.split("-") for x in contig.split("/")]
    for n,(a,b) in enumerate(sub_contigs):
      if a[0].isalpha():
        if n > 0:
          pa,pb = sub_contigs[n-1]
          if pa[0].isalpha() and a[0] == pa[0]:
            L_init += int(a[1:]) - int(pb) - 1
        L = int(b)-int(a[1:]) + 1
      else:
        L = int(b)
      R += range(L_init,L_init+L)  
      L_init += L
    return R
  
  contig_ranges = [get_range(x) for x in contigs]
  R,C = [],[]
  for n,r in enumerate(contig_ranges):
    R += r
    C += [alphabet_list[n]] * len(r)
  
  pdb_out = []
  r_, c_,n = None, None, 0 
  for line in pdb_str.split("\n"):
    if line[:4] == "ATOM":
      c = line[21:22]
      r = int(line[22:22+5])
      if r_ is None: r_ = r
      if c_ is None: c_ = c
      if r != r_ or c != c_:
        n += 1
        r_,c_ = r,c
      pdb_out.append("%s%s%4i%s" % (line[:21],C[n],R[n],line[26:]))
    if line[:5] == "MODEL" or line[:3] == "TER" or line[:6] == "ENDMDL":
      pdb_out.append(line)
      r_, c_,n = None, None, 0 
  return "\n".join(pdb_out)